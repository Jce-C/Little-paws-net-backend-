"""Trace citizen adoption creation without disclosing the applicant's notes."""
from unittest.mock import patch

from django.utils import timezone
from django.test import Client, override_settings
from rest_framework.test import APIClient

from adoption.models import SolicitudAdopcion
from animals.models import CustodiaMascota, Mascota
from core.models import Ciudad, Fundacion, UsuarioRol
from seguridad.autorizacion import invalidar
from seguridad.models import EventoSeguridad, RevisionPanel
from seguridad.tests import BaseRBAC, valor


class SolicitudAuditoriaTests(BaseRBAC):
    url = "/api/adopcion/solicitudes/"

    def setUp(self):
        city, _ = Ciudad.objects.get_or_create(nombre="Riohacha", departamento="La Guajira")
        self.foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit="QA-AUDIT-ADOPCION")
        self.pet = Mascota.objects.create(
            nombre="Solicitud auditable QA", descripcion_especie="Perro",
            estado_mascota=valor("estado_mascota", "En adopción"),
        )
        CustodiaMascota.objects.create(
            mascota=self.pet, fundacion=self.foundation,
            usuario_registrador=self.ana, fecha_inicio=timezone.now(),
        )
        self.client_api = APIClient()
        self.client_api.force_authenticate(self.ciudadano)
        self.payload = {"id_mascota": self.pet.pk, "observaciones": "Nota privada de la persona QA"}

    def eventos(self):
        return EventoSeguridad.objects.filter(accion="adopcion.participar", recurso="adopcion")

    def test_creation_is_audited_once_with_actor_entity_and_safe_transition(self):
        before = RevisionPanel.objects.get(pk=1).version
        response = self.client_api.post(self.url, self.payload)
        self.assertEqual(response.status_code, 201)
        event = self.eventos().get()
        self.assertEqual(event.actor_id, self.ciudadano.pk)
        self.assertEqual(event.entidad_id, self.entidad.pk)
        self.assertEqual(event.objeto_id, response.data["id_solicitud_adopcion"])
        self.assertEqual(event.datos["mascota_id"], self.pet.pk)
        self.assertEqual(event.datos["nuevo"], "Pendiente")
        self.assertIsNone(event.datos["anterior"])
        self.assertEqual(event.datos["_contexto"]["permiso"], "adopcion.participar")
        self.assertNotIn(self.payload["observaciones"], str(event.datos))
        self.assertNotIn("observaciones", event.datos)
        self.assertGreater(RevisionPanel.objects.get(pk=1).version, before)

    def test_duplicate_pending_request_does_not_duplicate_creation_or_audit(self):
        self.assertEqual(self.client_api.post(self.url, self.payload).status_code, 201)
        response = self.client_api.post(self.url, self.payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(SolicitudAdopcion.objects.filter(mascota=self.pet).count(), 1)
        self.assertEqual(self.eventos().count(), 1)

    @override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
    def test_panel_uses_the_same_creation_event_without_a_generic_duplicate(self):
        browser = Client()
        browser.force_login(self.ciudadano)
        response = browser.post("/panel/areas/adopciones/?accion=solicitar-adopcion", self.payload)
        self.assertEqual(response.status_code, 302)
        application = SolicitudAdopcion.objects.get(mascota=self.pet)
        event = self.eventos().get(objeto_id=application.pk)
        self.assertEqual(event.datos["_contexto"]["operacion_panel"], "solicitar-adopcion")
        self.assertFalse(EventoSeguridad.objects.filter(
            accion="negocio.operacion", datos__operacion="solicitar-adopcion",
        ).exists())

    def test_anonymous_request_creates_neither_application_nor_success_event(self):
        self.assertEqual(APIClient().post(self.url, self.payload).status_code, 401)
        self.assertFalse(SolicitudAdopcion.objects.filter(mascota=self.pet).exists())
        self.assertFalse(self.eventos().exists())

    def test_revoked_role_cannot_create_an_application_or_success_event(self):
        UsuarioRol.objects.filter(usuario=self.ciudadano).update(fecha_revocacion=timezone.now())
        invalidar()
        self.assertEqual(self.client_api.post(self.url, self.payload).status_code, 403)
        self.assertFalse(SolicitudAdopcion.objects.filter(mascota=self.pet).exists())
        self.assertFalse(self.eventos().exists())

    def test_unavailable_pet_does_not_create_application_or_success_event(self):
        self.pet.dueno = self.otro
        self.pet.save(update_fields=["dueno"])
        self.assertEqual(self.client_api.post(self.url, self.payload).status_code, 400)
        self.assertFalse(SolicitudAdopcion.objects.filter(mascota=self.pet).exists())
        self.assertFalse(self.eventos().exists())

    def test_audit_failure_rolls_back_application_but_records_failed_attempt(self):
        before = RevisionPanel.objects.get(pk=1).version
        with patch("adoption.api.auditar", side_effect=RuntimeError("QA audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.client_api.post(self.url, self.payload)
        self.assertFalse(SolicitudAdopcion.objects.filter(mascota=self.pet).exists())
        self.assertFalse(self.eventos().exists())
        failure = EventoSeguridad.objects.get(accion="operacion.fallida", actor=self.ciudadano)
        self.assertEqual(failure.datos["_contexto"]["resultado"], "FALLIDA")
        self.assertGreater(RevisionPanel.objects.get(pk=1).version, before)

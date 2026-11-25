from unittest.mock import patch

from rest_framework.test import APIClient

from accounts.models import Usuario
from seguridad.models import EventoSeguridad
from seguridad.tests import BaseRBAC


class PerfilPropioMovilTests(BaseRBAC):
    path = "/api/auth/perfil/"

    def test_actualiza_solo_su_identidad_y_audita_campos_sin_telefono(self):
        other = Usuario.objects.get(pk=self.otro.pk)
        response = self.cliente(self.ciudadano).patch(self.path, {"nombre": "Nombre propio QA", "telefono": "+57 300 123 4567"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nombre"], "Nombre propio QA")
        self.assertEqual(response.data["email"], self.ciudadano.email)
        self.assertEqual(response["Cache-Control"], "no-store")
        other.refresh_from_db()
        self.assertEqual(other.nombre, self.otro.nombre)
        event = EventoSeguridad.objects.get(accion="perfil.actualizar", actor=self.ciudadano)
        self.assertEqual(event.objeto_id, self.ciudadano.pk)
        self.assertEqual(event.datos["campos"], ["nombre", "telefono"])
        self.assertNotIn("+57 300 123 4567", str(event.datos))

    def test_rechaza_cambiar_identidad_roles_o_credenciales_como_parte_del_perfil(self):
        client = self.cliente(self.ciudadano)
        original = self.ciudadano.nombre
        for field, value in [("id_usuario", self.otro.pk), ("email", "otra@example.invalid"), ("is_superuser", True), ("is_staff", True), ("password", "Never-Apply-This-QA"), ("roles", [])]:
            with self.subTest(field=field):
                self.assertEqual(client.patch(self.path, {"nombre": "No aplicar", field: value}, format="json").status_code, 400)
        self.ciudadano.refresh_from_db()
        self.assertEqual(self.ciudadano.nombre, original)
        self.assertFalse(self.ciudadano.is_superuser)
        self.assertFalse(EventoSeguridad.objects.filter(accion="perfil.actualizar", actor=self.ciudadano).exists())

    def test_validacion_y_borrado_explicito_del_telefono_sin_tocar_nombre(self):
        client = self.cliente(self.ciudadano)
        for data in [{}, {"nombre": " "}, {"nombre": "x" * 151}, {"telefono": "abc"}, {"telefono": "123"}, {"telefono": "1234567890123456"}]:
            self.assertEqual(client.patch(self.path, data, format="json").status_code, 400)
        self.assertEqual(client.patch(self.path, {"telefono": "3001234567"}, format="json").status_code, 200)
        self.assertEqual(client.patch(self.path, {"telefono": ""}, format="json").status_code, 200)
        self.ciudadano.refresh_from_db()
        self.assertEqual(self.ciudadano.telefono, "")
        self.assertNotEqual(self.ciudadano.nombre, " ")

    def test_anonimo_denegado_y_lecturas_no_cacheables(self):
        anonymous = APIClient()
        self.assertEqual(anonymous.patch(self.path, {"nombre": "No aplicar"}, format="json").status_code, 401)
        self.assertEqual(anonymous.get(self.path).status_code, 401)
        response = self.cliente(self.ciudadano).get(self.path)
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(set(response.data), {"id_usuario", "email", "nombre", "telefono", "reintentos_seguros", "evaluacion_adopcion"})

    def test_cuenta_desactivada_se_rechaza_incluso_si_la_autenticacion_era_anterior(self):
        client = self.cliente(self.ciudadano)
        before = self.ciudadano.nombre
        Usuario.objects.filter(pk=self.ciudadano.pk).update(is_active=False)
        response = client.patch(self.path, {"nombre": "No aplicar QA"}, format="json")
        self.assertEqual(response.status_code, 403)
        self.ciudadano.refresh_from_db()
        self.assertEqual(self.ciudadano.nombre, before)

    def test_guardar_mismos_datos_no_duplica_auditoria_y_fallo_auditoria_revierte(self):
        client = self.cliente(self.ciudadano)
        client.patch(self.path, {"nombre": self.ciudadano.nombre}, format="json")
        self.assertFalse(EventoSeguridad.objects.filter(accion="perfil.actualizar", actor=self.ciudadano).exists())
        before = self.ciudadano.nombre
        with patch("seguridad.servicios.auditar", side_effect=RuntimeError("Fallo sintético QA")):
            with self.assertRaises(RuntimeError):
                client.patch(self.path, {"nombre": "Revertir QA"}, format="json")
        self.ciudadano.refresh_from_db()
        self.assertEqual(self.ciudadano.nombre, before)

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Usuario
from animals.models import CustodiaMascota, Especie, Mascota, Raza
from core.models import (
    Ciudad, EntidadMiembro, EntidadMiembroRol, EntidadVerificable,
    Fundacion, Permiso, Rol, UsuarioRol, ValorMaestro,
)

from .models import HistorialEstadoAdopcion, SolicitudAdopcion


class ModelosAdopcionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.solicitante = Usuario.objects.create_user(
            email="adoptante@example.invalid",
            password="Clave-Segura-2026",
            nombre="Adoptante",
        )
        cls.gestor = Usuario.objects.create_user(
            email="gestor-adopcion@example.invalid",
            password="Clave-Segura-2026",
            nombre="Gestor Adopcion",
        )
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        ciudad = Ciudad.objects.create(nombre="Ciudad Adopcion", departamento="Pruebas")
        entidad = EntidadVerificable.objects.create(nombre="Fundacion Adopcion", estado_verificacion=verificada)
        cls.fundacion = Fundacion.objects.create(entidad=entidad, nit="NIT-ADOPCION", ciudad=ciudad)
        especie = Especie.objects.get(nombre="Canino")
        raza = Raza.objects.get(especie=especie, nombre="Mestizo")
        cls.mascota = Mascota.objects.create(
            raza=raza,
            nombre="Nala",
            estado_mascota=ValorMaestro.objects.get(tipo__nombre="estado_mascota", nombre="En adopción"),
        )
        cls.estado_pendiente = ValorMaestro.objects.get(
            tipo__nombre="estado_solicitud_adopcion",
            nombre="Pendiente",
        )

    def test_catalogos_y_permiso_base_de_adopcion(self):
        estados = set(
            ValorMaestro.objects.filter(tipo__nombre="estado_solicitud_adopcion")
            .values_list("nombre", flat=True)
        )
        self.assertEqual(estados, {"Pendiente", "Aprobada", "Rechazada", "Cancelada"})
        self.assertTrue(Permiso.objects.filter(codigo="adopcion.resolver").exists())

    def test_solicitud_registra_estado_inicial_e_historial(self):
        solicitud = SolicitudAdopcion.objects.create(
            mascota=self.mascota,
            usuario_adoptante=self.solicitante,
            estado_adopcion=self.estado_pendiente,
            observaciones="Quiero adoptar a Nala",
        )
        HistorialEstadoAdopcion.objects.create(
            solicitud=solicitud,
            estado_nuevo=self.estado_pendiente,
            usuario_actor=self.solicitante,
            observacion="Creacion de la solicitud",
        )
        self.assertEqual(solicitud.estado_adopcion.nombre, "Pendiente")
        self.assertEqual(HistorialEstadoAdopcion.objects.filter(solicitud=solicitud).count(), 1)


class SolicitudAdopcionAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.solicitante = Usuario.objects.create_user(
            email="api-adoptante@example.invalid",
            password="Clave-Segura-2026",
            nombre="API Adoptante",
        )
        cls.gestor = Usuario.objects.create_user(
            email="api-gestor@example.invalid",
            password="Clave-Segura-2026",
            nombre="API Gestor",
        )
        cls.ajeno = Usuario.objects.create_user(
            email="api-ajeno@example.invalid",
            password="Clave-Segura-2026",
            nombre="API Ajeno",
        )
        cls.otro_adoptante = Usuario.objects.create_user(
            email="api-adoptante-2@example.invalid",
            password="Clave-Segura-2026",
            nombre="Otro Adoptante",
        )
        cls.admin = Usuario.objects.create_user(
            email="api-admin@example.invalid",
            password="Clave-Segura-2026",
            nombre="API Administrador",
        )
        UsuarioRol.objects.create(usuario=cls.admin, rol=Rol.objects.get(codigo="ADMIN_PLATAFORMA"))
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        ciudad = Ciudad.objects.create(nombre="Ciudad API Adopcion", departamento="Pruebas")
        entidad = EntidadVerificable.objects.create(nombre="Fundacion API Adopcion", estado_verificacion=verificada)
        cls.fundacion = Fundacion.objects.create(entidad=entidad, nit="NIT-API-ADOPCION", ciudad=ciudad)
        miembro = EntidadMiembro.objects.create(entidad=entidad, usuario=cls.gestor)
        EntidadMiembroRol.objects.create(miembro=miembro, rol=Rol.objects.get(codigo="GESTOR_FUNDACION"))
        especie = Especie.objects.get(nombre="Canino")
        raza = Raza.objects.get(especie=especie, nombre="Mestizo")
        cls.mascota = Mascota.objects.create(
            raza=raza,
            nombre="Mora",
            estado_mascota=ValorMaestro.objects.get(tipo__nombre="estado_mascota", nombre="En adopción"),
        )
        CustodiaMascota.objects.create(
            mascota=cls.mascota,
            fundacion=cls.fundacion,
            fecha_inicio=timezone.now(),
            usuario_registrador=cls.gestor,
        )

    def setUp(self):
        self.api = APIClient()

    def test_solicitud_en_ingles_con_estado_localizado(self):
        self.api.force_authenticate(user=self.solicitante)
        respuesta = self.api.post(reverse("adopcion_listar_crear"), {
            "id_mascota": self.mascota.pk,
            "observaciones": "I can care for this pet",
        }, format="json", HTTP_ACCEPT_LANGUAGE="en")
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        self.assertEqual(respuesta.data["estado"], "Pending")
        self.assertEqual(respuesta.data["observaciones"], "I can care for this pet")
        detalle = self.api.get(
            reverse("adopcion_detalle", args=[respuesta.data["id_solicitud_adopcion"]]),
            HTTP_ACCEPT_LANGUAGE="en",
        )
        self.assertEqual(detalle.data["historial"][0]["estado_nuevo"], "Pending")

    def test_error_de_adopcion_en_ingles(self):
        self.api.force_authenticate(user=self.solicitante)
        respuesta = self.api.post(reverse("adopcion_listar_crear"), {
            "id_mascota": 999999,
        }, format="json", HTTP_ACCEPT_LANGUAGE="en")
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.data["detalle"], "Pet not found")

    def test_crear_solicitud_crea_historial(self):
        self.api.force_authenticate(user=self.solicitante)
        respuesta = self.api.post(reverse("adopcion_listar_crear"), {
            "id_mascota": self.mascota.pk,
            "observaciones": "Tengo espacio y experiencia",
        }, format="json")
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        solicitud = SolicitudAdopcion.objects.get(pk=respuesta.data["id_solicitud_adopcion"])
        self.assertEqual(solicitud.estado_adopcion.nombre, "Pendiente")
        self.assertEqual(solicitud.observaciones, "Tengo espacio y experiencia")
        self.assertEqual(HistorialEstadoAdopcion.objects.filter(solicitud=solicitud).count(), 1)

    def test_solicitante_y_fundacion_consultan_la_solicitud(self):
        self.api.force_authenticate(user=self.solicitante)
        creada = self.api.post(reverse("adopcion_listar_crear"), {
            "id_mascota": self.mascota.pk,
        }, format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        detalle = reverse("adopcion_detalle", args=[creada.data["id_solicitud_adopcion"]])
        self.assertEqual(self.api.get(detalle).status_code, 200)
        self.api.force_authenticate(user=self.gestor)
        como_fundacion = self.api.get(detalle)
        self.assertEqual(como_fundacion.status_code, 200, como_fundacion.data)
        self.assertEqual(len(como_fundacion.data["historial"]), 1)
        self.api.force_authenticate(user=self.ajeno)
        self.assertEqual(self.api.get(detalle).status_code, 404)

    def test_no_permite_duplicar_solicitud_pendiente(self):
        self.api.force_authenticate(user=self.solicitante)
        datos = {"id_mascota": self.mascota.pk}
        self.assertEqual(self.api.post(reverse("adopcion_listar_crear"), datos).status_code, 201)
        duplicada = self.api.post(reverse("adopcion_listar_crear"), datos)
        self.assertEqual(duplicada.status_code, 400)
        self.assertEqual(SolicitudAdopcion.objects.filter(mascota=self.mascota).count(), 1)

    def test_filtro_mascota_invalido_devuelve_400(self):
        self.api.force_authenticate(user=self.solicitante)
        respuesta = self.api.get(reverse("adopcion_listar_crear"), {"id_mascota": "invalido"})
        self.assertEqual(respuesta.status_code, 400)

    def _crear_solicitud(self, usuario):
        self.api.force_authenticate(user=usuario)
        respuesta = self.api.post(reverse("adopcion_listar_crear"), {"id_mascota": self.mascota.pk}, format="json")
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        return respuesta.data["id_solicitud_adopcion"]

    def test_gestor_aprueba_y_cierra_otras_solicitudes(self):
        aprobada_id = self._crear_solicitud(self.solicitante)
        cancelada_id = self._crear_solicitud(self.otro_adoptante)
        self.api.force_authenticate(user=self.gestor)
        respuesta = self.api.post(reverse("adopcion_resolver", args=[aprobada_id]), {
            "estado": "Aprobada", "observacion": "Entrevista y visita satisfactorias",
        }, format="json")
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        self.assertEqual(SolicitudAdopcion.objects.get(pk=aprobada_id).estado_adopcion.nombre, "Aprobada")
        self.assertEqual(SolicitudAdopcion.objects.get(pk=cancelada_id).estado_adopcion.nombre, "Cancelada")
        self.assertEqual(HistorialEstadoAdopcion.objects.filter(solicitud_id=aprobada_id).count(), 2)
        self.assertEqual(HistorialEstadoAdopcion.objects.filter(solicitud_id=cancelada_id).count(), 2)
        self.mascota.refresh_from_db()
        self.assertEqual(self.mascota.dueno_id, self.solicitante.pk)
        self.assertEqual(self.mascota.estado_mascota.nombre, "Adoptada")
        self.assertIsNotNone(CustodiaMascota.objects.get(mascota=self.mascota).fecha_fin)
        self.assertEqual(self.api.get(reverse("adopcion_detalle", args=[aprobada_id])).status_code, 200)

    def test_gestor_rechaza_sin_cambiar_mascota(self):
        solicitud_id = self._crear_solicitud(self.solicitante)
        self.api.force_authenticate(user=self.gestor)
        respuesta = self.api.post(reverse("adopcion_resolver", args=[solicitud_id]), {
            "estado": "Rechazada", "observacion": "No cumple las condiciones de adopción",
        }, format="json")
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        self.mascota.refresh_from_db()
        self.assertIsNone(self.mascota.dueno_id)
        self.assertEqual(self.mascota.estado_mascota.nombre, "En adopción")
        self.assertEqual(SolicitudAdopcion.objects.get(pk=solicitud_id).estado_adopcion.nombre, "Rechazada")

    def test_solicitante_y_ajeno_no_pueden_resolver(self):
        solicitud_id = self._crear_solicitud(self.solicitante)
        ruta = reverse("adopcion_resolver", args=[solicitud_id])
        datos = {"estado": "Aprobada", "observacion": "Intento no autorizado"}
        self.assertEqual(self.api.post(ruta, datos, format="json").status_code, 403)
        self.api.force_authenticate(user=self.ajeno)
        self.assertEqual(self.api.post(ruta, datos, format="json").status_code, 403)
        self.assertEqual(SolicitudAdopcion.objects.get(pk=solicitud_id).estado_adopcion.nombre, "Pendiente")

    def test_admin_global_puede_resolver_con_observacion(self):
        solicitud_id = self._crear_solicitud(self.solicitante)
        self.api.force_authenticate(user=self.admin)
        respuesta = self.api.post(reverse("adopcion_resolver", args=[solicitud_id]), {
            "estado": "Rechazada", "observacion": "Resolución excepcional documentada",
        }, format="json")
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        self.assertEqual(SolicitudAdopcion.objects.get(pk=solicitud_id).estado_adopcion.nombre, "Rechazada")

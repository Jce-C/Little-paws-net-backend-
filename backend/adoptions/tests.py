from datetime import timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Usuario
from animals.models import CustodiaMascota, Especie, Mascota, Raza
from core.models import (
    Ciudad, EntidadMiembro, EntidadMiembroRol, EntidadVerificable,
    Fundacion, Permiso, Rol, ValorMaestro,
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
            fundacion=self.fundacion,
            usuario_solicitante=self.solicitante,
            estado_solicitud=self.estado_pendiente,
            observacion_solicitante="Quiero adoptar a Nala",
        )
        HistorialEstadoAdopcion.objects.create(
            solicitud=solicitud,
            estado_nuevo=self.estado_pendiente,
            usuario_actor=self.solicitante,
            observacion="Creacion de la solicitud",
        )
        self.assertEqual(solicitud.estado_solicitud.nombre, "Pendiente")
        self.assertEqual(HistorialEstadoAdopcion.objects.filter(solicitud=solicitud).count(), 1)

    def test_fecha_resolucion_no_puede_anteceder_solicitud(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SolicitudAdopcion.objects.create(
                    mascota=self.mascota,
                    fundacion=self.fundacion,
                    usuario_solicitante=self.solicitante,
                    estado_solicitud=self.estado_pendiente,
                    fecha_resolucion=timezone.now() - timedelta(days=1),
                    usuario_resolutor=self.gestor,
                )


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

    def test_crear_solicitud_deriva_fundacion_y_crea_historial(self):
        self.api.force_authenticate(user=self.solicitante)
        respuesta = self.api.post(reverse("adopcion_listar_crear"), {
            "id_mascota": self.mascota.pk,
            "observacion_solicitante": "Tengo espacio y experiencia",
        }, format="json")
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        solicitud = SolicitudAdopcion.objects.get(pk=respuesta.data["id_solicitud_adopcion"])
        self.assertEqual(solicitud.fundacion, self.fundacion)
        self.assertEqual(solicitud.estado_solicitud.nombre, "Pendiente")
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

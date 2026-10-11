from datetime import timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from accounts.models import Usuario
from animals.models import Especie, Mascota, Raza
from core.models import Ciudad, EntidadVerificable, Fundacion, Permiso, ValorMaestro

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

"""El esquema del fondo impide importes no válidos desde la base de datos."""

from decimal import Decimal

from cryptography.fernet import Fernet
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from accounts.models import Usuario
from core.models import Ciudad, EntidadVerificable, Fundacion, TipoMaestro, ValorMaestro

from .models import DonacionGeneral, FondoExterno, SolicitudEmergencia


class ModelosFondoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            email="donante-fondo@example.invalid", password="Clave-Segura-2026", nombre="Donante Fondo",
        )
        cls.fondo = FondoExterno.objects.create(
            nombre="Fondo de prueba",
            datos_transferencia_cifrados=Fernet(Fernet.generate_key()).encrypt(b"cuenta-de-prueba"),
        )
        tipo_donacion, _ = TipoMaestro.objects.get_or_create(nombre="estado_donacion")
        cls.comprometida, _ = ValorMaestro.objects.get_or_create(tipo=tipo_donacion, nombre="Comprometida")
        tipo_emergencia, _ = TipoMaestro.objects.get_or_create(nombre="estado_emergencia")
        cls.pendiente, _ = ValorMaestro.objects.get_or_create(tipo=tipo_emergencia, nombre="Pendiente")
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        ciudad = Ciudad.objects.create(nombre="Ciudad Fondo", departamento="Pruebas")
        entidad = EntidadVerificable.objects.create(nombre="Fundación Fondo", estado_verificacion=verificada)
        cls.fundacion = Fundacion.objects.create(entidad=entidad, nit="NIT-FONDO-TEST", ciudad=ciudad)

    def test_donacion_guarda_importe_y_fecha(self):
        donacion = DonacionGeneral.objects.create(
            fondo_externo=self.fondo,
            usuario_donante=self.usuario,
            estado_donacion=self.comprometida,
            monto_comprometido=Decimal("15000.00"),
        )
        self.assertEqual(donacion.monto_comprometido, Decimal("15000.00"))
        self.assertIsNotNone(donacion.fecha_compromiso)

    def test_no_acepta_donacion_de_importe_no_positivo(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DonacionGeneral.objects.create(
                    fondo_externo=self.fondo,
                    usuario_donante=self.usuario,
                    estado_donacion=self.comprometida,
                    monto_comprometido=Decimal("0.00"),
                )

    def test_emergencia_requiere_motivo_e_importe_positivo(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SolicitudEmergencia.objects.create(
                    fundacion=self.fundacion,
                    fondo_externo=self.fondo,
                    estado_emergencia=self.pendiente,
                    motivo="",
                    monto_solicitado=Decimal("100.00"),
                )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SolicitudEmergencia.objects.create(
                    fundacion=self.fundacion,
                    fondo_externo=self.fondo,
                    estado_emergencia=self.pendiente,
                    motivo="Atención veterinaria urgente",
                    monto_solicitado=Decimal("0.00"),
                )
        solicitud = SolicitudEmergencia.objects.create(
            fundacion=self.fundacion,
            fondo_externo=self.fondo,
            estado_emergencia=self.pendiente,
            motivo="Atención veterinaria urgente",
            monto_solicitado=Decimal("100.00"),
        )
        self.assertLessEqual(solicitud.fecha_solicitud, timezone.now())

"""El esquema del fondo impide importes no válidos desde la base de datos."""

import os
from decimal import Decimal
from unittest.mock import patch

from cryptography.fernet import Fernet
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Usuario
from core.models import (
    Ciudad, EntidadVerificable, Fundacion, Permiso, Rol, RolPermiso,
    TipoMaestro, UsuarioRol, ValorMaestro,
)

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

    def test_catalogos_y_permisos_no_son_globales_por_defecto(self):
        self.assertEqual(
            set(ValorMaestro.objects.filter(tipo__nombre="estado_donacion").values_list("nombre", flat=True)),
            {"Comprometida", "Confirmada", "Rechazada", "Cancelada"},
        )
        self.assertEqual(
            set(ValorMaestro.objects.filter(tipo__nombre="estado_distribucion").values_list("nombre", flat=True)),
            {"Reportada", "Confirmada", "Rechazada"},
        )
        self.assertEqual(Permiso.objects.filter(codigo__startswith="distribucion.").count(), 2)
        admin = Rol.objects.get(codigo="ADMIN_PLATAFORMA")
        gestor = Rol.objects.get(codigo="GESTOR_FUNDACION")
        self.assertTrue(RolPermiso.objects.filter(rol=admin, permiso__codigo="donacion.confirmar").exists())
        self.assertFalse(RolPermiso.objects.filter(rol=admin, permiso__codigo="distribucion.confirmar").exists())
        self.assertTrue(RolPermiso.objects.filter(rol=gestor, permiso__codigo="distribucion.confirmar").exists())
        self.assertFalse(RolPermiso.objects.filter(rol=gestor, permiso__codigo="donacion.confirmar").exists())

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


class FondoExternoAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = Usuario.objects.create_user(
            email="admin-fondo@example.invalid", password="Clave-Segura-2026", nombre="Admin Fondo",
        )
        cls.usuario = Usuario.objects.create_user(
            email="usuario-fondo@example.invalid", password="Clave-Segura-2026", nombre="Usuario Fondo",
        )
        UsuarioRol.objects.create(usuario=cls.admin, rol=Rol.objects.get(codigo="ADMIN_PLATAFORMA"))

    def setUp(self):
        self.api = APIClient()
        self.clave = Fernet.generate_key().decode("ascii")

    def test_solo_administrador_configura_fondo_y_datos_quedan_cifrados(self):
        ruta = reverse("fondo_listar_crear")
        datos = {
            "nombre": "Fondo Solidario",
            "instrucciones_transferencia": "Banco de prueba, cuenta 123-456",
        }
        self.assertEqual(self.api.get(ruta).status_code, 401)
        self.api.force_authenticate(user=self.usuario)
        self.assertEqual(self.api.post(ruta, datos, format="json").status_code, 403)
        self.api.force_authenticate(user=self.admin)
        with patch.dict(os.environ, {"LPN_DATA_KEY": self.clave}):
            respuesta = self.api.post(ruta, datos, format="json")
            self.assertEqual(respuesta.status_code, 201, respuesta.data)
            fondo = FondoExterno.objects.get(pk=respuesta.data["id_fondo_externo"])
            self.assertNotIn(b"123-456", bytes(fondo.datos_transferencia_cifrados))
            self.assertEqual(set(respuesta.data), {"id_fondo_externo", "nombre"})
            listado = self.api.get(ruta)
            self.assertNotIn("instrucciones_transferencia", str(listado.data))
            self.api.force_authenticate(user=self.usuario)
            instrucciones = self.api.get(reverse("fondo_instrucciones", args=[fondo.pk]))
            self.assertEqual(instrucciones.status_code, 200, instrucciones.data)
            self.assertEqual(
                instrucciones.data["instrucciones_transferencia"],
                datos["instrucciones_transferencia"],
            )

    def test_no_duplica_nombre_de_fondo(self):
        self.api.force_authenticate(user=self.admin)
        ruta = reverse("fondo_listar_crear")
        with patch.dict(os.environ, {"LPN_DATA_KEY": self.clave}):
            primera = self.api.post(ruta, {
                "nombre": "Fondo Unico", "instrucciones_transferencia": "Cuenta de prueba",
            }, format="json")
            segunda = self.api.post(ruta, {
                "nombre": "fondo unico", "instrucciones_transferencia": "Otra cuenta",
            }, format="json")
        self.assertEqual(primera.status_code, 201, primera.data)
        self.assertEqual(segunda.status_code, 400, segunda.data)
        self.assertEqual(FondoExterno.objects.filter(nombre__iexact="Fondo Unico").count(), 1)

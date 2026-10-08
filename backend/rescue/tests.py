from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import Usuario
from core.models import (
    CapacidadFundacion, Ciudad, EntidadMiembro, EntidadMiembroRol,
    EntidadVerificable, Fundacion, Rol, ValorMaestro,
)

from .models import CasoRescate, HistorialEstadoCaso, HistorialEstadoReporte, Reporte


class FlujoRescateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reportante = Usuario.objects.create_user(
            email="reportante@example.invalid", password="Clave-Segura-2026", nombre="Reportante",
        )
        cls.gestor = Usuario.objects.create_user(
            email="gestor@example.invalid", password="Clave-Segura-2026", nombre="Gestor",
        )
        cls.ajeno = Usuario.objects.create_user(
            email="ajeno@example.invalid", password="Clave-Segura-2026", nombre="Ajeno",
        )
        cls.ciudad = Ciudad.objects.create(nombre="Ciudad Prueba", departamento="Pruebas")
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        entidad = EntidadVerificable.objects.create(nombre="Fundación Prueba", estado_verificacion=verificada)
        cls.fundacion = Fundacion.objects.create(entidad=entidad, nit="NIT-PRUEBA", ciudad=cls.ciudad)
        cls.capacidad = CapacidadFundacion.objects.create(
            fundacion=cls.fundacion, cupos_totales=1, usuario_actualizador=cls.gestor,
        )
        miembro = EntidadMiembro.objects.create(entidad=entidad, usuario=cls.gestor)
        EntidadMiembroRol.objects.create(miembro=miembro, rol=Rol.objects.get(codigo="GESTOR_FUNDACION"))
        cls.tipo_reporte = ValorMaestro.objects.get(tipo__nombre="tipo_reporte", nombre="Rescate")

    def setUp(self):
        self.api = APIClient()

    def crear_reporte(self, usuario=None):
        if usuario:
            self.api.force_authenticate(user=usuario)
        respuesta = self.api.post(reverse("reporte_crear"), {
            "tipo_reporte": self.tipo_reporte.pk,
            "descripcion": "Animal herido en la vía",
            "latitud": "4.609710", "longitud": "-74.081750",
        }, format="json")
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        return respuesta

    def test_reporte_anonimo_con_codigo_privado_y_auditoria(self):
        respuesta = self.crear_reporte()
        reporte = Reporte.objects.get(pk=respuesta.data["id_reporte"])
        self.assertNotEqual(respuesta.data["codigo_gestion"], reporte.codigo_gestion_hash)
        self.assertEqual(HistorialEstadoReporte.objects.filter(reporte=reporte).count(), 1)
        gestion = reverse("reporte_gestion_anonima", args=[reporte.pk])
        self.assertEqual(self.api.post(gestion, {"codigo_gestion": "incorrecto", "cerrar": True}).status_code, 403)
        cierre = self.api.post(gestion, {"codigo_gestion": respuesta.data["codigo_gestion"], "cerrar": True})
        self.assertEqual(cierre.status_code, 200)
        reporte.refresh_from_db()
        self.assertEqual(reporte.estado_reporte.nombre, "Cerrado")
        self.assertEqual(HistorialEstadoReporte.objects.filter(reporte=reporte).count(), 2)

    @patch("rescue.services.fundacion_cubre_reporte", return_value=True)
    def test_aceptacion_autorizada_y_cierre_actualizan_cupo(self, cobertura):
        reporte_id = self.crear_reporte(self.reportante).data["id_reporte"]
        aceptar = reverse("reporte_aceptar", args=[reporte_id])
        self.api.force_authenticate(user=self.ajeno)
        self.assertEqual(self.api.post(aceptar, {"id_fundacion": self.fundacion.pk}).status_code, 400)
        self.api.force_authenticate(user=self.gestor)
        aceptado = self.api.post(aceptar, {"id_fundacion": self.fundacion.pk})
        self.assertEqual(aceptado.status_code, 201, aceptado.data)
        caso = CasoRescate.objects.get(pk=aceptado.data["id_caso"])
        self.capacidad.refresh_from_db()
        self.assertEqual(self.capacidad.cupos_ocupados, 1)
        self.assertEqual(HistorialEstadoCaso.objects.filter(caso=caso).count(), 1)
        cierre = self.api.post(reverse("caso_cerrar", args=[caso.pk]), {"estado": "Cerrado"})
        self.assertEqual(cierre.status_code, 200, cierre.data)
        self.capacidad.refresh_from_db()
        self.assertEqual(self.capacidad.cupos_ocupados, 0)
        self.assertEqual(HistorialEstadoCaso.objects.filter(caso=caso).count(), 2)
        self.assertEqual(Reporte.objects.get(pk=reporte_id).estado_reporte.nombre, "Cerrado")
        self.assertEqual(self.api.post(aceptar, {"id_fundacion": self.fundacion.pk}).status_code, 400)

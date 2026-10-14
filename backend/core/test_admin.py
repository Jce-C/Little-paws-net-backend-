"""Pruebas de carga supervisada y acceso de solo consulta en Django Admin."""

from decimal import Decimal

from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from accounts.models import Usuario
from animals.models import Especie, Mascota
from core.models import TipoMaestro, ValorMaestro
from rescue.models import HistorialEstadoReporte, Reporte, ReporteUbicacion


class PanelInternoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.operador = Usuario.objects.create_superuser(
            email="admin@example.invalid", password="Clave-Admin-2026!", nombre="Administración",
        )

    def setUp(self):
        self.client.force_login(self.operador)

    def test_modelos_del_proyecto_aparecen_en_admin(self):
        self.assertIn(Usuario, admin.site._registry)
        self.assertIn(Especie, admin.site._registry)
        self.assertIn(Mascota, admin.site._registry)
        self.assertIn(Reporte, admin.site._registry)
        respuesta = self.client.get(reverse("admin:index"))
        self.assertContains(respuesta, "Animals")
        self.assertContains(respuesta, "Rescue")

    def test_alta_de_catalogo_desde_admin(self):
        respuesta = self.client.post(reverse("admin:animals_especie_add"), {
            "nombre": "Gato", "descripcion": "Felino doméstico", "_save": "Guardar",
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Especie.objects.filter(nombre="Gato").exists())

    def test_alta_de_usuario_hashea_clave_y_no_concede_superusuario(self):
        respuesta = self.client.post(reverse("admin:accounts_usuario_add"), {
            "email": "nuevo@example.invalid", "nombre": "Usuario de prueba", "telefono": "",
            "password1": "ClaveNuevaSegura-2026!", "password2": "ClaveNuevaSegura-2026!",
            "_save": "Guardar",
        })
        self.assertEqual(respuesta.status_code, 302, respuesta.context and respuesta.context.get("adminform"))
        nuevo = Usuario.objects.get(email="nuevo@example.invalid")
        self.assertTrue(nuevo.check_password("ClaveNuevaSegura-2026!"))
        self.assertFalse(nuevo.is_staff)
        self.assertFalse(nuevo.is_superuser)

    def test_alta_de_reporte_crea_ubicacion_y_historial(self):
        tipo = ValorMaestro.objects.get(tipo__nombre="tipo_reporte", nombre="Rescate")
        respuesta = self.client.post(reverse("admin:rescue_reporte_add"), {
            "tipo_reporte": tipo.pk,
            "descripcion": "Gato herido encontrado cerca del parque",
            "contacto_reportante": "",
            "latitud": "4.609710", "longitud": "-74.081750", "_save": "Guardar",
        })
        self.assertEqual(respuesta.status_code, 302, respuesta.context and respuesta.context.get("adminform"))
        reporte = Reporte.objects.get()
        self.assertEqual(reporte.estado_reporte.nombre, "Pendiente")
        self.assertEqual(reporte.usuario_reportante, self.operador)
        self.assertEqual(ReporteUbicacion.objects.get(reporte=reporte).latitud, Decimal("4.609710"))
        self.assertEqual(HistorialEstadoReporte.objects.filter(reporte=reporte).count(), 1)

    def test_proceso_no_admite_edicion_directa(self):
        tipo = ValorMaestro.objects.get(tipo__nombre="tipo_reporte", nombre="Rescate")
        estado = ValorMaestro.objects.get(tipo__nombre="estado_reporte", nombre="Pendiente")
        reporte = Reporte.objects.create(
            tipo_reporte=tipo, estado_reporte=estado, descripcion="Original", usuario_reportante=self.operador,
        )
        ruta = reverse("admin:rescue_reporte_change", args=[reporte.pk])
        self.assertEqual(self.client.get(ruta).status_code, 200)
        respuesta = self.client.post(ruta, {"descripcion": "Alterado", "_save": "Guardar"})
        self.assertEqual(respuesta.status_code, 403)
        reporte.refresh_from_db()
        self.assertEqual(reporte.descripcion, "Original")

    def test_tipo_maestro_del_sistema_se_registra(self):
        self.assertIn(TipoMaestro, admin.site._registry)

    def test_listados_registrados_abren_sin_errores(self):
        apps = {"accounts", "core", "animals", "rescue", "adoptions", "funds", "commerce"}
        for modelo in admin.site._registry:
            if modelo._meta.app_label not in apps:
                continue
            with self.subTest(modelo=modelo.__name__):
                ruta = reverse(f"admin:{modelo._meta.app_label}_{modelo._meta.model_name}_changelist")
                self.assertEqual(self.client.get(ruta).status_code, 200)

    def test_detalle_usuario_no_muestra_hash_y_staff_no_adquiere_permiso(self):
        ruta = reverse("admin:accounts_usuario_change", args=[self.operador.pk])
        respuesta = self.client.get(ruta)
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, self.operador.password)

        soporte = Usuario.objects.create_user(
            email="soporte@example.invalid", password="Clave-Soporte-2026!",
            nombre="Soporte", is_staff=True,
        )
        self.client.force_login(soporte)
        listado = reverse("admin:accounts_usuario_changelist")
        self.assertEqual(self.client.get(listado).status_code, 403)

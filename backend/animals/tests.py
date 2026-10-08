from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Usuario
from core.models import (
    Ciudad, EntidadMiembro, EntidadMiembroRol, EntidadVerificable,
    Fundacion, Rol, ValorMaestro, Veterinario,
)
from rescue.models import CasoRescate, Reporte

from .models import CustodiaMascota, Especie, HistorialMedico, Mascota, Raza


class ExpedienteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gestor = Usuario.objects.create_user(
            email="custodio@example.invalid", password="Clave-Segura-2026", nombre="Custodio",
        )
        cls.profesional = Usuario.objects.create_user(
            email="vet@example.invalid", password="Clave-Segura-2026", nombre="Veterinario",
        )
        cls.ajeno = Usuario.objects.create_user(
            email="extraño@example.invalid", password="Clave-Segura-2026", nombre="Ajeno",
        )
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        ciudad = Ciudad.objects.create(nombre="Ciudad Médica", departamento="Prueba")
        entidad = EntidadVerificable.objects.create(nombre="Fundación Médica", estado_verificacion=verificada)
        cls.fundacion = Fundacion.objects.create(entidad=entidad, ciudad=ciudad, nit="NIT-MEDICO")
        miembro = EntidadMiembro.objects.create(entidad=entidad, usuario=cls.gestor)
        EntidadMiembroRol.objects.create(miembro=miembro, rol=Rol.objects.get(codigo="GESTOR_FUNDACION"))
        entidad_vet = EntidadVerificable.objects.create(nombre="Veterinario verificado", estado_verificacion=verificada)
        cls.veterinario = Veterinario.objects.create(
            entidad=entidad_vet, usuario_profesional=cls.profesional,
            registro_profesional="MAT-001",
        )
        especie = Especie.objects.get(nombre="Canino")
        raza = Raza.objects.get(especie=especie, nombre="Mestizo")
        cls.mascota = Mascota.objects.create(
            raza=raza, nombre="Luna",
            estado_mascota=ValorMaestro.objects.get(tipo__nombre="estado_mascota", nombre="En rescate"),
        )
        reporte = Reporte.objects.create(
            usuario_reportante=cls.ajeno, mascota=cls.mascota,
            tipo_reporte=ValorMaestro.objects.get(tipo__nombre="tipo_reporte", nombre="Rescate"),
            estado_reporte=ValorMaestro.objects.get(tipo__nombre="estado_reporte", nombre="En atención"),
            descripcion="Rescate de Luna",
        )
        cls.caso = CasoRescate.objects.create(
            reporte=reporte, fundacion=cls.fundacion,
            estado_caso=ValorMaestro.objects.get(tipo__nombre="estado_caso", nombre="En atención"),
            usuario_ultimo_cambio=cls.gestor,
        )

    def setUp(self):
        self.api = APIClient()

    def test_fundacion_identifica_mascota_del_caso(self):
        reporte = Reporte.objects.create(
            usuario_reportante=self.ajeno,
            tipo_reporte=ValorMaestro.objects.get(tipo__nombre="tipo_reporte", nombre="Rescate"),
            estado_reporte=ValorMaestro.objects.get(tipo__nombre="estado_reporte", nombre="En atención"),
            descripcion="Animal sin identificar",
        )
        caso = CasoRescate.objects.create(
            reporte=reporte, fundacion=self.fundacion,
            estado_caso=ValorMaestro.objects.get(tipo__nombre="estado_caso", nombre="En atención"),
            usuario_ultimo_cambio=self.gestor,
        )
        url = reverse("caso_mascota_crear", args=[caso.pk])
        datos = {"raza": Raza.objects.get(nombre="Mestizo", especie__nombre="Canino").pk, "nombre": "Sol"}
        self.api.force_authenticate(user=self.ajeno)
        self.assertEqual(self.api.post(url, datos).status_code, 400)
        self.api.force_authenticate(user=self.gestor)
        respuesta = self.api.post(url, datos)
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        reporte.refresh_from_db()
        self.assertEqual(reporte.mascota_id, respuesta.data["id_mascota"])
        self.assertEqual(self.api.post(url, datos).status_code, 400)
        self.assertEqual(self.api.post(reverse("custodia_registrar", args=[caso.pk])).status_code, 201)

    def test_qr_no_da_acceso_sin_autorizacion_y_regeneracion_revoca_anterior(self):
        self.api.force_authenticate(user=self.gestor)
        custodia = self.api.post(reverse("custodia_registrar", args=[self.caso.pk]))
        self.assertEqual(custodia.status_code, 201, custodia.data)
        qr_url = reverse("expediente_qr", args=[self.mascota.pk])
        primer_qr = self.api.post(qr_url, {})
        self.assertEqual(primer_qr.status_code, 201, primer_qr.data)
        token_inicial = primer_qr.data["codigo_qr"]
        self.api.force_authenticate(user=self.profesional)
        consultar = reverse("expediente_consultar", args=[self.mascota.pk])
        self.assertEqual(self.api.post(consultar, {"codigo_qr": token_inicial}).status_code, 403)
        self.api.force_authenticate(user=self.gestor)
        autorizacion = self.api.post(reverse("expediente_autorizar", args=[self.mascota.pk]), {
            "id_veterinario": self.veterinario.pk, "dias": 7,
        })
        self.assertEqual(autorizacion.status_code, 201, autorizacion.data)
        segundo_qr = self.api.post(qr_url, {})
        self.assertEqual(segundo_qr.status_code, 201, segundo_qr.data)
        self.api.force_authenticate(user=self.profesional)
        self.assertEqual(self.api.post(consultar, {"codigo_qr": token_inicial}).status_code, 403)
        actual = segundo_qr.data["codigo_qr"]
        registro = self.api.post(reverse("expediente_registrar", args=[self.mascota.pk]), {
            "codigo_qr": actual, "detalle": "Control de heridas",
            "fecha_atencion": timezone.now().isoformat(),
        })
        self.assertEqual(registro.status_code, 201, registro.data)
        self.assertEqual(self.api.post(consultar, {"codigo_qr": actual}).status_code, 200)
        self.api.force_authenticate(user=self.ajeno)
        self.assertEqual(self.api.post(consultar, {"codigo_qr": actual}).status_code, 403)
        self.api.force_authenticate(user=self.gestor)
        externa = self.api.post(reverse("expediente_registrar_externo", args=[self.mascota.pk]), {
            "nombre_veterinario_externo": "Dra. Externa",
            "registro_profesional_externo": "MAT-EXT-001",
            "detalle": "Atención externa revisada",
            "fecha_atencion": timezone.now().isoformat(),
        })
        self.assertEqual(externa.status_code, 201, externa.data)
        self.assertEqual(HistorialMedico.objects.filter(mascota=self.mascota).count(), 2)
        CustodiaMascota.objects.filter(mascota=self.mascota, fecha_fin__isnull=True).update(
            fecha_fin=timezone.now(),
        )
        self.api.force_authenticate(user=self.profesional)
        self.assertEqual(self.api.post(consultar, {"codigo_qr": actual}).status_code, 403)

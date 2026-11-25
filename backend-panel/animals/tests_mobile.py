from django.utils import timezone
from rest_framework.test import APIClient

from animals.models import CodigoQRExpediente, CustodiaMascota, HistorialMedico, Mascota
from core.models import Ciudad, Fundacion, Permiso
from seguridad.tests import BaseRBAC, valor


class MisMascotasMovilTests(BaseRBAC):
    def setUp(self):
        self.pet = Mascota.objects.create(dueno=self.ciudadano, nombre="Mascota propia QA", descripcion_especie="Perro", estado_mascota=valor("estado_mascota", "Con dueño"))
        self.other_pet = Mascota.objects.create(dueno=self.otro, nombre="Mascota ajena QA", descripcion_especie="Gato", estado_mascota=self.pet.estado_mascota)
        HistorialMedico.objects.create(mascota=self.pet, detalle="Registro clínico sintético QA", usuario_registrador=self.admin,
            usuario_verificador=self.admin, nombre_veterinario_externo="Profesional externo QA", registro_profesional_externo="QA-000", fecha_atencion=timezone.now())

    def test_listado_propio_no_acepta_otra_identidad_y_no_incluye_clinica(self):
        response = self.cliente(self.ciudadano).get("/api/mascotas/mias/", {"usuario_id": self.otro.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id_mascota"] for row in response.data], [self.pet.pk])
        self.assertNotIn("detalle", response.data[0])
        self.assertFalse(response.data[0]["custodia_vigente"])
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(APIClient().get("/api/mascotas/mias/").status_code, 401)

    def test_expediente_existente_solo_muestra_datos_a_quien_tiene_acceso(self):
        path = f"/api/seguridad/operaciones/registros/expediente/{self.pet.pk}/"
        own = self.cliente(self.ciudadano).get(path)
        self.assertEqual(own.status_code, 200)
        self.assertEqual(own.data["atenciones_recientes_maximo_50"][0]["detalle"], "Registro clínico sintético QA")
        self.assertEqual(own["Cache-Control"], "no-store")
        self.assertEqual(self.cliente(self.otro).get(path).status_code, 403)
        self.assertEqual(APIClient().get(path).status_code, 401)

    def test_revocar_participacion_retira_listado_y_expediente(self):
        Permiso.objects.filter(codigo="mascotas.participar").update(activo=False)
        client = self.cliente(self.ciudadano)
        self.assertEqual(client.get("/api/mascotas/mias/").status_code, 403)
        self.assertEqual(client.get(f"/api/seguridad/operaciones/registros/expediente/{self.pet.pk}/").status_code, 403)

    def test_custodia_en_conflicto_se_indica_sin_ocultar_la_ficha_asociada(self):
        city, _ = Ciudad.objects.get_or_create(nombre="Riohacha", departamento="La Guajira")
        foundation = Fundacion.objects.create(entidad=self.entidad, nit="QA-MOVIL-CUSTODIA", ciudad=city)
        CustodiaMascota.objects.create(mascota=self.pet, fundacion=foundation, usuario_registrador=self.ana, fecha_inicio=timezone.now())
        response = self.cliente(self.ciudadano).get("/api/mascotas/mias/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]["custodia_vigente"])
        self.assertEqual(self.cliente(self.ciudadano).get(f"/api/seguridad/operaciones/registros/expediente/{self.pet.pk}/").status_code, 400)

    def test_qr_propio_se_emite_sin_exponer_clinica_ni_guardar_token(self):
        import hashlib
        response = self.cliente(self.ciudadano).post(f"/api/mascotas/{self.pet.pk}/qr/", {}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(set(response.data), {"id_qr", "codigo", "expira"})
        qr = CodigoQRExpediente.objects.get(pk=response.data["id_qr"])
        self.assertEqual(qr.codigo_hash, hashlib.sha256(response.data["codigo"].encode("ascii")).hexdigest())
        public = APIClient().get(f"/api/qr/{response.data['codigo']}/")
        self.assertEqual(public.status_code, 200)
        self.assertEqual(set(public.data), {"id_mascota", "nombre"})
        self.assertEqual(public["Cache-Control"], "no-store")

    def test_qr_ajeno_y_anonimo_no_se_pueden_generar(self):
        path = f"/api/mascotas/{self.pet.pk}/qr/"
        self.assertEqual(self.cliente(self.otro).post(path, {}, format="json").status_code, 400)
        self.assertEqual(APIClient().post(path, {}, format="json").status_code, 401)
        self.assertFalse(CodigoQRExpediente.objects.filter(mascota=self.pet).exists())

    def test_reemplazo_y_vencimiento_rechazan_codigo_anterior(self):
        from datetime import timedelta
        client = self.cliente(self.ciudadano)
        path = f"/api/mascotas/{self.pet.pk}/qr/"
        first = client.post(path, {}, format="json").data
        second = client.post(path, {}, format="json").data
        self.assertNotEqual(first["codigo"], second["codigo"])
        public = APIClient()
        revoked = public.get(f"/api/qr/{first['codigo']}/")
        self.assertEqual(revoked.status_code, 404)
        self.assertEqual(revoked["Cache-Control"], "no-store")
        self.assertEqual(public.get(f"/api/qr/{second['codigo']}/").status_code, 200)
        CodigoQRExpediente.objects.filter(pk=second["id_qr"]).update(fecha_creacion=timezone.now() - timedelta(days=2), fecha_expiracion=timezone.now() - timedelta(seconds=1))
        self.assertEqual(public.get(f"/api/qr/{second['codigo']}/").status_code, 404)

    def test_poseer_qr_no_otorga_escritura_clinica(self):
        code = self.cliente(self.ciudadano).post(f"/api/mascotas/{self.pet.pk}/qr/", {}, format="json").data["codigo"]
        path = f"/api/qr/{code}/atenciones/"
        data = {"detalle": "Intento QA no autorizado", "fecha_atencion": timezone.now().isoformat()}
        before = HistorialMedico.objects.filter(mascota=self.pet).count()
        self.assertEqual(APIClient().post(path, data, format="json").status_code, 401)
        self.assertEqual(self.cliente(self.otro).post(path, data, format="json").status_code, 400)
        self.assertEqual(HistorialMedico.objects.filter(mascota=self.pet).count(), before)

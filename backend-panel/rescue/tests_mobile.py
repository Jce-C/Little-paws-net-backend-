from rest_framework.test import APIClient

from core.models import Ciudad, Fundacion, Permiso, ValorMaestro
from rescue.models import CasoRescate, HistorialEstadoReporte, Reporte
from seguridad.tests import BaseRBAC, valor


class ReportesMovilTests(BaseRBAC):
    def setUp(self):
        self.ciudad, _ = Ciudad.objects.get_or_create(nombre="Riohacha", departamento="La Guajira", defaults={"activo": True})
        self.tipo = ValorMaestro.objects.filter(tipo__nombre="tipo_reporte").first()

    def test_opciones_publicas_buscan_ciudades_activas_sin_descargar_catalogo_completo(self):
        Ciudad.objects.create(nombre="Riohacha inactiva QA", departamento="QA", activo=False)
        client = APIClient()
        self.assertEqual(client.get("/api/reportes/opciones/").data["ciudades"], [])
        response = client.get("/api/reportes/opciones/", {"ciudad": "Rioha"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.ciudad.pk, [row["id_ciudad"] for row in response.data["ciudades"]])
        self.assertFalse(any(row["nombre"].endswith("QA") for row in response.data["ciudades"]))
        self.assertTrue(response.data["tipos"])
        self.assertEqual(set(response.data), {"tipos", "ciudades"})

    def test_seguimiento_solo_devuelve_propios_y_no_credenciales_ni_contactos(self):
        mine = Reporte.objects.create(usuario_reportante=self.ciudadano, tipo_reporte=self.tipo, estado_reporte=valor("estado_reporte", "Pendiente"), descripcion="Animal encontrado QA", contacto_reportante="Privado QA", ciudad=self.ciudad)
        Reporte.objects.create(usuario_reportante=self.otro, tipo_reporte=self.tipo, estado_reporte=mine.estado_reporte, descripcion="Reporte de otra persona QA")
        url = "/api/reportes/mios/"
        self.assertEqual(APIClient().get(url).status_code, 401)
        response = self.cliente(self.ciudadano).get(url, {"usuario": self.otro.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id_reporte"] for row in response.data], [mine.pk])
        self.assertIsNone(response.data[0]["caso"])
        self.assertNotIn("contacto_reportante", response.data[0])
        self.assertNotIn("codigo_gestion_hash", response.data[0])

    def test_crear_reporte_usa_permiso_configurable_y_se_consulta_en_mis_reportes(self):
        client = self.cliente(self.ciudadano)
        data = {"tipo_reporte": self.tipo.pk, "ciudad_id": self.ciudad.pk, "barrio": "Barrio QA", "direccion": "Ubicación sintética QA", "descripcion": "Animal que requiere atención QA"}
        response = client.post("/api/reportes/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("codigo_gestion", response.data)
        self.assertEqual(client.get("/api/reportes/mios/").data[0]["id_reporte"], response.data["id_reporte"])
        Permiso.objects.filter(codigo="reportes.participar").update(activo=False)
        before = Reporte.objects.count()
        denied = self.cliente(self.ciudadano).post("/api/reportes/", data, format="json")
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(Reporte.objects.count(), before)

    def test_seguimiento_incluye_el_caso_solo_para_su_reportante(self):
        report = Reporte.objects.create(usuario_reportante=self.ciudadano, tipo_reporte=self.tipo, estado_reporte=valor("estado_reporte", "Pendiente"), descripcion="Reporte QA")
        foundation = Fundacion.objects.create(entidad=self.entidad, nit="QA-MOVIL-RESCATE", ciudad=self.ciudad)
        case = CasoRescate.objects.create(reporte=report, fundacion=foundation, estado_caso=ValorMaestro.objects.filter(tipo__nombre="estado_caso").first(), usuario_ultimo_cambio=self.ana)
        own = self.cliente(self.ciudadano).get("/api/reportes/mios/")
        self.assertEqual(own.data[0]["caso"]["id_caso"], case.pk)
        self.assertEqual(own.data[0]["caso"]["fundacion"], self.entidad.nombre)
        self.assertEqual(self.cliente(self.otro).get("/api/reportes/mios/").data, [])

    def test_reporte_anonimo_entrega_clave_solo_en_su_confirmacion(self):
        data = {"tipo_reporte": self.tipo.pk, "ciudad_id": self.ciudad.pk, "barrio": "Barrio QA", "direccion": "Lugar sintético QA", "descripcion": "Animal encontrado QA"}
        response = APIClient().post("/api/reportes/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["codigo_gestion"])
        report = Reporte.objects.get(pk=response.data["id_reporte"])
        self.assertIsNone(report.usuario_reportante_id)
        self.assertNotEqual(report.codigo_gestion_hash, response.data["codigo_gestion"])
        self.assertEqual(self.cliente(self.ciudadano).get("/api/reportes/mios/").data, [])

    def _anonymous_report(self, address):
        client = APIClient(REMOTE_ADDR=address)
        data = {"tipo_reporte": self.tipo.pk, "ciudad_id": self.ciudad.pk, "barrio": "Sector QA", "direccion": "Referencia QA", "descripcion": "Descripción inicial QA"}
        result = client.post("/api/reportes/", data, format="json")
        self.assertEqual(result.status_code, 201)
        return client, Reporte.objects.get(pk=result.data["id_reporte"]), result.data["codigo_gestion"]

    def test_clave_anonima_invalida_no_modifica_y_valida_corrige(self):
        client, report, code = self._anonymous_report("127.0.2.81")
        url = f"/api/reportes/{report.pk}/gestion-anonima/"
        denied = client.post(url, {"codigo_gestion": "clave-invalida-QA", "descripcion": "Cambio no autorizado QA"}, format="json")
        self.assertEqual(denied.status_code, 403)
        report.refresh_from_db()
        self.assertEqual(report.descripcion, "Descripción inicial QA")
        result = client.post(url, {"codigo_gestion": code, "descripcion": "Descripción corregida QA", "contacto_reportante": "Contacto QA"}, format="json")
        self.assertEqual(result.status_code, 200)
        report.refresh_from_db()
        self.assertEqual(report.descripcion, "Descripción corregida QA")
        self.assertEqual(report.contacto_reportante, "Contacto QA")
        self.assertNotIn("codigo_gestion", result.data)
        clear = client.post(url, {"codigo_gestion": code, "contacto_reportante": ""}, format="json")
        self.assertEqual(clear.status_code, 200)
        report.refresh_from_db()
        self.assertEqual(report.contacto_reportante, "")

    def test_cierre_anonimo_registra_estado_y_no_se_puede_repetir(self):
        client, report, code = self._anonymous_report("127.0.2.82")
        url = f"/api/reportes/{report.pk}/gestion-anonima/"
        self.assertEqual(client.post(url, {"codigo_gestion": code, "cerrar": True}, format="json").status_code, 200)
        report.refresh_from_db()
        self.assertEqual(report.estado_reporte.nombre, "Cerrado")
        self.assertEqual(HistorialEstadoReporte.objects.filter(reporte=report).count(), 1)
        self.assertEqual(client.post(url, {"codigo_gestion": code, "cerrar": True}, format="json").status_code, 409)
        self.assertEqual(HistorialEstadoReporte.objects.filter(reporte=report).count(), 1)

    def test_caso_aceptado_impide_modificacion_con_clave_anonima(self):
        client, report, code = self._anonymous_report("127.0.2.83")
        foundation = Fundacion.objects.create(entidad=self.entidad, nit="QA-ANONIMO-ACEPTADO", ciudad=self.ciudad)
        CasoRescate.objects.create(reporte=report, fundacion=foundation, estado_caso=ValorMaestro.objects.filter(tipo__nombre="estado_caso").first(), usuario_ultimo_cambio=self.ana)
        url = f"/api/reportes/{report.pk}/gestion-anonima/"
        result = client.post(url, {"codigo_gestion": code, "descripcion": "Cambio posterior QA"}, format="json")
        self.assertEqual(result.status_code, 409)
        report.refresh_from_db()
        self.assertEqual(report.descripcion, "Descripción inicial QA")


    def test_edicion_auditada_sin_clave_contacto_ni_texto_y_repeticion_sin_evento(self):
        from seguridad.models import EventoSeguridad
        import json
        client, report, code = self._anonymous_report("127.0.2.84")
        url = f"/api/reportes/{report.pk}/gestion-anonima/"
        body = {"codigo_gestion": code, "descripcion": "Descripcion privada sintética", "contacto_reportante": "contacto-personal.invalid"}
        first = client.post(url, body, format="json")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first["Cache-Control"], "no-store")
        events = EventoSeguridad.objects.filter(accion="reporte.gestion_anonima", objeto_id=report.pk)
        self.assertEqual(events.count(), 1)
        from seguridad.web.dashboard import descripcion_evento
        from seguridad.web.presentacion_eventos import informacion_evento
        self.assertIn("Actualizó un reporte", descripcion_evento(events.get()))
        self.assertIn("Contacto privado", informacion_evento(events.get()))
        payload = json.dumps(events.get().datos)
        for secret in (code, body["descripcion"], body["contacto_reportante"]):
            self.assertNotIn(secret, payload)
        report.refresh_from_db()
        updated = report.fecha_actualizacion
        self.assertEqual(client.post(url, body, format="json").status_code, 200)
        report.refresh_from_db()
        self.assertEqual(report.fecha_actualizacion, updated)
        self.assertEqual(events.count(), 1)

    def test_errores_privados_no_se_cachean_y_reporte_con_titular_rechaza_clave(self):
        client, report, code = self._anonymous_report("127.0.2.85")
        url = f"/api/reportes/{report.pk}/gestion-anonima/"
        denied = client.post(url, {"codigo_gestion": "incorrecta", "descripcion": "Cambio"}, format="json")
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied["Cache-Control"], "no-store")
        report.usuario_reportante = self.ana
        report.codigo_gestion_hash = ""
        report.save(update_fields=["usuario_reportante", "codigo_gestion_hash"])
        denied = client.post(url, {"codigo_gestion": code, "descripcion": "Cambio"}, format="json")
        self.assertEqual(denied.status_code, 404)
        self.assertEqual(denied["Cache-Control"], "no-store")


    def test_creacion_rechaza_identidad_inyectada_y_datos_incompletos_sin_filas(self):
        client = APIClient(REMOTE_ADDR="127.0.3.80")
        base = {"tipo_reporte": self.tipo.pk, "ciudad_id": self.ciudad.pk, "barrio": "Sector QA", "direccion": "Referencia QA", "descripcion": "Situación QA"}
        before = Reporte.objects.count()
        for body in [dict(base, usuario_reportante=self.otro.pk), dict(base, descripcion=""), dict(base, latitud="11.0")]:
            result = client.post("/api/reportes/", body, format="json")
            self.assertEqual(result.status_code, 400)
            self.assertEqual(result["Cache-Control"], "no-store")
            self.assertEqual(Reporte.objects.count(), before)

    def test_tipo_desactivado_y_ciudad_inactiva_no_permiten_crear(self):
        client = APIClient(REMOTE_ADDR="127.0.3.81")
        base = {"tipo_reporte": self.tipo.pk, "ciudad_id": self.ciudad.pk, "barrio": "Sector QA", "direccion": "Referencia QA", "descripcion": "Situación QA"}
        self.ciudad.activo = False
        self.ciudad.save(update_fields=["activo"])
        self.assertEqual(client.post("/api/reportes/", base, format="json").status_code, 400)
        self.ciudad.activo = True
        self.ciudad.save(update_fields=["activo"])
        self.tipo.tipo.activo = False
        self.tipo.tipo.save(update_fields=["activo"])
        self.assertEqual(client.post("/api/reportes/", base, format="json").status_code, 400)

    def test_foto_exige_autorizacion_y_se_persiste_en_webp_acotada(self):
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        from rescue.models import FotoReporte
        image = io.BytesIO()
        Image.new("RGB", (1600, 1100), "orange").save(image, format="JPEG")
        client = APIClient(REMOTE_ADDR="127.0.3.82")
        base = {"tipo_reporte": self.tipo.pk, "ciudad_id": self.ciudad.pk, "barrio": "Sector QA", "direccion": "Referencia QA", "descripcion": "Situación QA", "contacto_reportante": "contacto-privado.invalid"}
        before = Reporte.objects.count()
        denied = client.post("/api/reportes/", {**base, "archivo": SimpleUploadedFile("animal.jpg", image.getvalue(), content_type="image/jpeg")}, format="multipart")
        self.assertEqual(denied.status_code, 400)
        self.assertEqual(Reporte.objects.count(), before)
        result = client.post("/api/reportes/", {**base, "confirmar_foto_publica": "true", "archivo": SimpleUploadedFile("animal.jpg", image.getvalue(), content_type="image/jpeg")}, format="multipart")
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result["Cache-Control"], "no-store")
        photo = FotoReporte.objects.get(reporte_id=result.data["id_reporte"])
        self.assertLessEqual(photo.tamano_bytes, 128 * 1024)
        self.assertLessEqual(max(photo.ancho, photo.alto), 960)
        with Image.open(io.BytesIO(bytes(photo.contenido))) as stored:
            self.assertEqual(stored.format, "WEBP")
            self.assertFalse(stored.getexif())
        self.assertNotIn("contacto_reportante", result.data)

from rest_framework.test import APIClient

from rescue.models import Reporte
from seguridad.models import PublicacionReporte
from seguridad.tests import BaseRBAC, valor


class ReportesPublicosPaginadosTests(BaseRBAC):
    url = "/api/reportes/publicos/"

    def setUp(self):
        self.tipo = valor("tipo_reporte", "Mascota perdida")
        self.estado = valor("estado_reporte", "Pendiente")
        # Separar la identidad de throttling de los ensayos de registro/reporte.
        self.public = APIClient(REMOTE_ADDR="127.0.44.91")

    def reports(self, count):
        previous = Reporte.objects.order_by("-pk").values_list("pk", flat=True).first() or 0
        Reporte.objects.bulk_create([
            Reporte(tipo_reporte=self.tipo, estado_reporte=self.estado,
                    descripcion=f"Reporte público sintético QA {index}",
                    contacto_reportante="Contacto privado QA",
                    codigo_gestion_hash="hash-privado-QA")
            for index in range(count)
        ])
        # MySQL no devuelve los IDs de bulk_create; releer las filas del ensayo.
        return list(Reporte.objects.filter(pk__gt=previous).order_by("pk"))

    def test_recorre_mas_de_cien_sin_duplicados_ni_campos_privados(self):
        expected = {r.pk for r in self.reports(105)}
        received = []
        params = {}
        while True:
            response = self.public.get(self.url, params)
            self.assertEqual(response.status_code, 200)
            self.assertLessEqual(len(response.data["results"]), 20)
            for row in response.data["results"]:
                self.assertEqual(set(row), {"id_reporte", "descripcion", "tipo_reporte__nombre", "estado_reporte__nombre", "ciudad", "foto", "caso"})
                received.append(row["id_reporte"])
            cursor = response.data["next_cursor"]
            if cursor is None:
                break
            self.assertLess(len(received), 106)
            params = {"antes": cursor}
        self.assertEqual(set(received), expected)
        self.assertEqual(len(received), len(expected))
        self.assertEqual(received, sorted(received, reverse=True))

    def test_ocultacion_y_busqueda_se_aplican_antes_del_limite(self):
        old = self.reports(1)[0]
        old.descripcion = "Coincidencia remota sintética QA"
        old.save(update_fields=["descripcion"])
        recent = self.reports(101)
        hidden = recent[-1]
        hidden.descripcion = old.descripcion
        hidden.save(update_fields=["descripcion"])
        PublicacionReporte.objects.create(reporte=hidden, oculta=True)
        result = self.public.get(self.url, {"buscar": "remota"})
        self.assertEqual(result.status_code, 200)
        self.assertEqual([r["id_reporte"] for r in result.data["results"]], [old.pk])
        self.assertIsNone(result.data["next_cursor"])

    def test_retirar_publicacion_entre_paginas_no_la_vuelve_a_exponer(self):
        rows = self.reports(23)
        first = self.public.get(self.url).data
        PublicacionReporte.objects.create(reporte=rows[0], oculta=True)
        inserted = self.reports(1)[0]
        second = self.public.get(self.url, {"antes": first["next_cursor"]}).data
        ids = [r["id_reporte"] for r in second["results"]]
        self.assertNotIn(rows[0].pk, ids)
        self.assertNotIn(inserted.pk, ids)
        self.assertIsNone(second["next_cursor"])

    def test_parametros_invalidos_y_busqueda_vacia(self):
        for cursor in ("-1", "0", "1.2", "https://example.invalid/", "9" * 30, "１２"):
            self.assertEqual(self.public.get(self.url, {"antes": cursor}).status_code, 400)
        self.assertEqual(self.public.get(self.url, {"buscar": "x" * 101}).status_code, 400)
        self.assertEqual(self.public.get(self.url).data, {"results": [], "next_cursor": None})

    def test_contrato_legacy_conserva_lista_acotada_y_ocultacion(self):
        rows = self.reports(102)
        PublicacionReporte.objects.create(reporte=rows[-1], oculta=True)
        response = self.public.get("/api/seguridad/operaciones/reportes-publicos/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 100)
        self.assertNotIn(rows[-1].pk, [r["id_reporte"] for r in response.data])

    def test_lectura_publica_no_habilita_escritura_y_usa_una_consulta(self):
        self.reports(25)
        with self.assertNumQueries(1):
            result = self.public.get(self.url)
        self.assertEqual(result.status_code, 200)
        denied = self.public.post(self.url, {"descripcion": "Cambio no permitido QA"}, format="json")
        self.assertEqual(denied.status_code, 405)
        self.assertEqual(Reporte.objects.count(), 25)

    def test_paginar_no_agota_el_presupuesto_anonimo_de_acceso(self):
        client = APIClient(REMOTE_ADDR="127.0.44.92")
        for _ in range(21):
            self.assertEqual(client.get(self.url).status_code, 200)
        self.assertEqual(client.get("/api/reportes/opciones/").status_code, 200)

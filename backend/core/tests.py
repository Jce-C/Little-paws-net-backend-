from django.test import TestCase
from django.urls import reverse


class CatalogosTests(TestCase):
    def test_catalogos_publicos_contienen_estados_de_reporte(self):
        response = self.client.get(reverse("catalogos"))
        self.assertEqual(response.status_code, 200)
        reporte = next(item for item in response.json() if item["tipo"] == "estado_reporte")
        self.assertIn("Pendiente", [valor["nombre"] for valor in reporte["valores"]])

    def test_catalogos_en_ingles_mantienen_tipo_estable(self):
        response = self.client.get(reverse("catalogos"), HTTP_ACCEPT_LANGUAGE="en")
        self.assertEqual(response.status_code, 200)
        reporte = next(item for item in response.json() if item["tipo"] == "estado_reporte")
        self.assertIn("Pending", [valor["nombre"] for valor in reporte["valores"]])
        self.assertEqual(response["Content-Language"], "en")

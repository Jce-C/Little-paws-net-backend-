from django.test import TestCase
from django.urls import reverse


class CatalogosTests(TestCase):
    def test_catalogos_publicos_contienen_estados_de_reporte(self):
        response = self.client.get(reverse("catalogos"))
        self.assertEqual(response.status_code, 200)
        reporte = next(item for item in response.json() if item["tipo"] == "estado_reporte")
        self.assertIn("Pendiente", [valor["nombre"] for valor in reporte["valores"]])

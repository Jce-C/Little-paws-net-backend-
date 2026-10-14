from django.test import SimpleTestCase
from django.urls import reverse


class SaludSinBaseTests(SimpleTestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("health"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_idioma_predeterminado_espanol(self):
        response = self.client.get(reverse("idiomas"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["idioma_actual"], "es")
        self.assertEqual(response["Content-Language"], "es")
        self.assertIn("Accept-Language", response.get("Vary", ""))

    def test_ingles_por_accept_language(self):
        response = self.client.get(
            reverse("idiomas"), HTTP_HOST="localhost", HTTP_ACCEPT_LANGUAGE="en-US,en;q=0.9",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["idioma_actual"], "en")
        self.assertEqual(response.json()["mensaje"], "Available languages")
        self.assertEqual(response["Content-Language"], "en")

    def test_idioma_no_admitido_vuelve_a_espanol(self):
        response = self.client.get(
            reverse("idiomas"), HTTP_HOST="localhost", HTTP_ACCEPT_LANGUAGE="fr",
        )
        self.assertEqual(response.json()["idioma_actual"], "es")


class PublicEndpointsTests(SimpleTestCase):
    def test_index_and_health_are_public(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/api/health/").json(), {"status": "ok"})

    def test_demo_summary_is_not_exposed_on_other_databases(self):
        self.assertEqual(self.client.get("/api/demo/resumen/").status_code, 404)

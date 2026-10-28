from django.test import SimpleTestCase
from django.urls import reverse


class SaludSinBaseTests(SimpleTestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("health"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

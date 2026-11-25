from django.test import TestCase
from django.urls import reverse


class SaludSinBaseTests(TestCase):
    def test_ip_forwarded_only_from_configured_railway_edge(self):
        from django.test import RequestFactory, override_settings
        from seguridad.web.acceso import ip_cliente
        request = RequestFactory().get("/", REMOTE_ADDR="127.0.0.1", HTTP_X_REAL_IP="203.0.113.9")
        with override_settings(LPN_TRUST_RAILWAY_PROXY=False):
            self.assertEqual(ip_cliente(request), "127.0.0.1")
        with override_settings(LPN_TRUST_RAILWAY_PROXY=True):
            self.assertEqual(ip_cliente(request), "203.0.113.9")
            request.META["HTTP_X_REAL_IP"] = "not-an-ip"
            self.assertEqual(ip_cliente(request), "127.0.0.1")
    def test_health_endpoint(self):
        response = self.client.get(reverse("health"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_root_is_a_landing_without_login_form(self):
        response = self.client.get("/", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguridad/web/landing.html')
        self.assertContains(response, reverse('panel:login'))
        self.assertNotContains(response, 'id="login-form"')
        self.assertNotContains(response, '/jsi18n/')
        self.assertNotContains(response, 'fondo-escritorio.svg')

    def test_railway_probe_accepts_http_but_login_requires_https(self):
        from django.test import override_settings
        with override_settings(SECURE_SSL_REDIRECT=True, SECURE_REDIRECT_EXEMPT=[r"^api/health/$"]):
            self.assertEqual(self.client.get(reverse("health"), HTTP_HOST="localhost").status_code, 200)
            self.assertEqual(self.client.get(reverse("panel:login"), HTTP_HOST="localhost").status_code, 301)

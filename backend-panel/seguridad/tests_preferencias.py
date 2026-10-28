from django.test import Client, SimpleTestCase, override_settings
from django.utils.translation import override, gettext
from rest_framework.exceptions import ErrorDetail

from .i18n import traducir_error
from .tests import BaseRBAC


@override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class IdiomaVistaTests(BaseRBAC):
    def test_light_is_default_but_explicit_choices_are_preserved(self):
        browser = Client()
        self.assertContains(browser.get("/panel/login/"), 'data-theme="light"')
        for selected in ("dark", "system"):
            browser.cookies["lpn_tema"] = selected
            self.assertContains(browser.get("/panel/login/"), f'data-theme="{selected}"')

    def test_dark_theme_is_validated_and_rendered_before_styles(self):
        browser = Client()
        response = browser.post("/panel/preferencias/", {"tema": "dark", "next": "/panel/login/"})
        self.assertEqual(response.cookies["lpn_tema"].value, "dark")
        self.assertTrue(response.cookies["lpn_tema"]["httponly"])
        page = browser.get("/panel/login/")
        self.assertContains(page, 'data-theme="dark"')
        self.assertContains(page, '<meta name="color-scheme" content="dark">')
        self.assertContains(page, "seguridad/tema.css")
        html = page.content.decode()
        self.assertLess(html.index('data-theme="dark"'), html.index('rel="stylesheet"'))
        browser.cookies["lpn_tema"] = "unsupported"
        self.assertContains(browser.get("/panel/login/"), 'data-theme="light"')

    def test_theme_switch_and_reset_preserve_permissions(self):
        browser = Client()
        browser.force_login(self.admin)
        roles = list(self.admin.usuariorol_set.values_list("rol_id", flat=True))
        browser.post("/panel/preferencias/", {"tema": "dark", "contraste": "strong", "next": "/panel/"})
        page = browser.get("/panel/")
        self.assertContains(page, 'data-theme="dark"')
        self.assertContains(page, 'data-contrast="strong"')
        browser.post("/panel/preferencias/", {"restablecer": "1"})
        self.assertContains(browser.get("/panel/"), 'data-theme="light"')
        self.assertEqual(roles, list(self.admin.usuariorol_set.values_list("rol_id", flat=True)))

    def test_login_english_and_translated_validation(self):
        browser = Client()
        browser.cookies["lpn_language"] = "en"
        response = browser.get("/panel/login/")
        self.assertContains(response, 'lang="en"')
        self.assertContains(response, "Welcome to your space")
        self.assertContains(response, "Email address")
        self.assertContains(response, "Language and accessibility")
        response = browser.post("/panel/login/", {"email": "bad", "captcha": "wrong"})
        self.assertContains(response, "We couldn&#x27;t sign you in.", status_code=400)

    def test_set_language_cookie_persists_without_changing_roles(self):
        browser = Client()
        browser.force_login(self.admin)
        before = list(self.admin.usuariorol_set.values_list("rol_id", flat=True))
        response = browser.post("/i18n/setlang/", {"language": "en", "next": "/panel/"})
        self.assertEqual(response.cookies["lpn_language"].value, "en")
        self.assertRedirects(response, "/panel/", fetch_redirect_response=False)
        page = browser.get("/panel/modulos/usuarios/")
        self.assertContains(page, "New user")
        self.assertContains(page, "Security")
        self.assertEqual(before, list(self.admin.usuariorol_set.values_list("rol_id", flat=True)))

    def test_language_and_preferences_require_csrf(self):
        browser = Client(enforce_csrf_checks=True)
        self.assertEqual(browser.post("/i18n/setlang/", {"language": "en"}).status_code, 403)
        self.assertEqual(browser.post("/panel/preferencias/", {"texto": "large"}).status_code, 403)

    def test_preference_allowlist_persistence_and_reset(self):
        browser = Client()
        response = browser.post("/panel/preferencias/", {
            "texto": "largest", "contraste": "strong", "movimiento": "reduce", "next": "/panel/login/"})
        self.assertEqual(response.cookies["lpn_texto"].value, "largest")
        self.assertTrue(response.cookies["lpn_texto"]["httponly"])
        page = browser.get("/panel/login/")
        self.assertContains(page, 'data-text-size="largest"')
        self.assertContains(page, 'data-motion="reduce"')
        self.assertContains(page, 'data-contrast="strong"')
        browser.post("/panel/preferencias/", {"restablecer": "1"})
        self.assertContains(browser.get("/panel/login/"), 'data-text-size="normal"')
        browser.cookies["lpn_texto"] = 'bad" onclick="alert(1)'
        self.assertContains(browser.get("/panel/login/"), 'data-text-size="normal"')

    def test_no_open_redirect_or_language_mixed_catalog(self):
        browser = Client()
        response = browser.post("/panel/preferencias/", {"next": "https://example.org/", "texto": "unsupported"})
        self.assertRedirects(response, "/panel/login/", fetch_redirect_response=False)
        self.assertEqual(response.cookies["lpn_texto"].value, "normal")
        browser.cookies["lpn_language"] = "en"
        self.assertContains(browser.get("/jsi18n/"), "Changes saved.")
        browser.cookies["lpn_language"] = "es"
        self.assertNotContains(browser.get("/jsi18n/"), '"Cambios guardados.": "Changes saved."')


class ErrorTranslationTests(SimpleTestCase):
    def test_error_keys_codes_and_domain_identifiers_remain_stable(self):
        with override("en"):
            translated = traducir_error({"email": [ErrorDetail("El correo ya está registrado", code="unique")]})
            self.assertEqual(translated["email"][0], "This email is already registered")
            self.assertEqual(translated["email"][0].code, "unique")
            self.assertEqual(gettext("usuarios.ver"), "usuarios.ver")

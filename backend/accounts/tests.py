from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Usuario


class UsuarioSinBaseTests(SimpleTestCase):
    def test_password_no_se_guarda_en_claro(self):
        usuario = Usuario(email="prueba@example.invalid", nombre="Prueba")
        usuario.set_password("ClaveDePrueba-2026")
        self.assertNotEqual(usuario.password, "ClaveDePrueba-2026")
        self.assertTrue(usuario.check_password("ClaveDePrueba-2026"))


class RegistroIdiomaTests(TestCase):
    def test_correo_duplicado_en_ingles(self):
        Usuario.objects.create_user(
            email="duplicate@example.invalid", password="ClaveDePrueba-2026", nombre="Prueba",
        )
        respuesta = self.client.post(
            reverse("registro"),
            {"email": "duplicate@example.invalid", "nombre": "Otro", "password": "ClaveDePrueba-2026"},
            content_type="application/json", HTTP_ACCEPT_LANGUAGE="en",
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("already registered", str(respuesta.json()))

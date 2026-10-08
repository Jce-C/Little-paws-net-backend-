from django.test import SimpleTestCase

from .models import Usuario


class UsuarioSinBaseTests(SimpleTestCase):
    def test_password_no_se_guarda_en_claro(self):
        usuario = Usuario(email="prueba@example.invalid", nombre="Prueba")
        usuario.set_password("ClaveDePrueba-2026")
        self.assertNotEqual(usuario.password, "ClaveDePrueba-2026")
        self.assertTrue(usuario.check_password("ClaveDePrueba-2026"))

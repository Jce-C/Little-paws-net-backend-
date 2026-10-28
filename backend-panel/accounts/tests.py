from django.test import SimpleTestCase

from .models import Usuario


class UsuarioSinBaseTests(SimpleTestCase):
    def test_la_contrasena_se_guarda_como_hash(self):
        usuario = Usuario(email="prueba@example.com", nombre="Prueba")
        usuario.set_password("una-clave-de-prueba")

        self.assertNotEqual(usuario.password, "una-clave-de-prueba")
        self.assertTrue(usuario.check_password("una-clave-de-prueba"))
        self.assertFalse(usuario.check_password("otra-clave"))

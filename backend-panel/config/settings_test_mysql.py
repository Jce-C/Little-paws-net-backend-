"""Pruebas reales en un MySQL aislado. Nunca reutiliza la conexión del .env."""
import os

from .settings import *  # noqa: F403

test_port = int(os.environ["LPN_TEST_MYSQL_PORT"])
if os.environ["LPN_TEST_MYSQL_HOST"] != "127.0.0.1" or test_port == int(DATABASES["default"]["PORT"]):
    raise RuntimeError("Las pruebas requieren una instancia MySQL local y un puerto distinto al habitual")
DATABASES = {"default": {
    "ENGINE": "django.db.backends.mysql", "NAME": "lpn_rbac_sandbox",
    "USER": os.environ["LPN_TEST_MYSQL_USER"], "PASSWORD": os.environ["LPN_TEST_MYSQL_PASSWORD"],
    "HOST": "127.0.0.1", "PORT": str(test_port),
    "OPTIONS": {"charset": "utf8mb4"}, "TEST": {"NAME": "test_lpn_rbac_sandbox"},
}}
SECRET_KEY = "isolated-tests-only-not-for-deployment"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

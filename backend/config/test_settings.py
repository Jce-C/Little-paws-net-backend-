"""Pruebas aisladas: no crean ni modifican la base MySQL del equipo."""

from .settings import *  # noqa: F403,F401


DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
ALLOWED_HOSTS = [*ALLOWED_HOSTS, "testserver"]

"""Configuración explícita para el futuro servicio del panel; no modifica la API anterior."""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from .settings import *  # noqa: F403

DEBUG = False
LPN_TRUST_RAILWAY_PROXY = True
MIDDLEWARE = list(MIDDLEWARE)  # noqa: F405
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^api/health/$"]
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
if "healthcheck.railway.app" not in ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, "healthcheck.railway.app"]  # noqa: F405
DATABASES["default"]["CONN_MAX_AGE"] = 60  # noqa: F405
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # noqa: F405
DATABASES["default"]["OPTIONS"]["connect_timeout"] = 10  # noqa: F405
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
if os.getenv("RAILWAY_ENVIRONMENT") and not os.getenv("LPN_PRIVATE_ROOT"):
    raise ImproperlyConfigured("Configure LPN_PRIVATE_ROOT en un volumen privado persistente del panel")
LPN_PRIVATE_ROOT = Path(os.getenv("LPN_PRIVATE_ROOT", str(BASE_DIR / ".private-data")))  # noqa: F405

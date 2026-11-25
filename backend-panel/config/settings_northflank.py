"""Servicio público detrás del ingress HTTP de Northflank, sin proxy de Railway."""
import os
from django.core.exceptions import ImproperlyConfigured
from .settings_railway import *  # noqa: F403

LPN_TRUST_RAILWAY_PROXY = False
LPN_TRUST_NORTHFLANK_PROXY = True
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host != 'healthcheck.railway.app']  # noqa: F405
if not os.getenv('LPN_PRIVATE_ROOT'):  # noqa: F405
    raise ImproperlyConfigured('Configure LPN_PRIVATE_ROOT en un volumen persistente de Northflank')  # noqa: F405

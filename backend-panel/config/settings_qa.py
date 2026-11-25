"""Servidor de aceptación aislado; hereda la barrera de MySQL local de pruebas."""
from .settings_test_mysql import *
DATABASES['default']['NAME']='lpn_panel_qa_29'
DEBUG=True
ALLOWED_HOSTS = [*ALLOWED_HOSTS, '10.0.2.2']
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
LANGUAGE_COOKIE_SECURE=False

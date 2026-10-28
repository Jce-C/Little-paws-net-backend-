"""Rutas del fondo externo (responsable: María José)."""

from django.urls import path

from .api import DistribucionCrearView, DonacionCrearView, EmergenciaCrearView, FondosView


urlpatterns = [
    path("fondos/", FondosView.as_view(), name="fondos"),
    path("fondos/donaciones/", DonacionCrearView.as_view(), name="donacion_fondo_crear"),
    path("fundaciones/<int:fundacion_id>/emergencias/", EmergenciaCrearView.as_view(), name="emergencia_crear"),
    path("fondos/<int:fondo_id>/distribuciones/", DistribucionCrearView.as_view(), name="distribucion_crear"),
]

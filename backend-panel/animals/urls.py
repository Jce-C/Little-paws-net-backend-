"""Rutas del expediente veterinario."""

from django.urls import path

from .views import AtencionCrearView, AutorizarView, QRConsultarView, QRCrearView


urlpatterns = [
    path("mascotas/<int:mascota_id>/autorizaciones/", AutorizarView.as_view(), name="expediente_autorizar"),
    path("mascotas/<int:mascota_id>/qr/", QRCrearView.as_view(), name="qr_crear"),
    path("qr/<str:token>/", QRConsultarView.as_view(), name="qr_consultar"),
    path("qr/<str:token>/atenciones/", AtencionCrearView.as_view(), name="atencion_crear"),
]

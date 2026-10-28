"""Rutas del proceso de adopción (responsable: María José)."""

from django.urls import path

from .api import MascotasAdopcionView, SolicitudCrearView, SolicitudResolverView


urlpatterns = [
    path("adopcion/mascotas/", MascotasAdopcionView.as_view(), name="mascotas_adopcion"),
    path("adopcion/solicitudes/", SolicitudCrearView.as_view(), name="solicitud_adopcion_crear"),
    path("adopcion/solicitudes/<int:solicitud_id>/resolver/", SolicitudResolverView.as_view(), name="solicitud_adopcion_resolver"),
]

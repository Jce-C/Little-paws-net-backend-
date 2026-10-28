"""Rutas compartidas de catálogos y notificaciones."""

from django.urls import path

from .api import CatalogosView, LeerNotificacionView, MisNotificacionesView


urlpatterns = [
    path("catalogos/", CatalogosView.as_view(), name="catalogos"),
    path("notificaciones/", MisNotificacionesView.as_view(), name="mis_notificaciones"),
    path("notificaciones/<int:notificacion_id>/leer/", LeerNotificacionView.as_view(), name="notificacion_leer"),
]

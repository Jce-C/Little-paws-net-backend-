"""Seguimiento de adopciones sin edición directa de sus estados."""

from django.contrib import admin

from core.admin_base import SoloLecturaAdmin

from .models import HistorialEstadoAdopcion, SolicitudAdopcion


@admin.register(SolicitudAdopcion)
class SolicitudAdopcionAdmin(SoloLecturaAdmin):
    list_display = ("id_solicitud_adopcion", "mascota", "usuario_adoptante", "estado_adopcion", "fecha_solicitud")
    list_filter = ("estado_adopcion",)
    search_fields = ("mascota__nombre", "usuario_adoptante__email")


@admin.register(HistorialEstadoAdopcion)
class HistorialEstadoAdopcionAdmin(SoloLecturaAdmin):
    list_display = ("id_historial_adopcion", "solicitud", "estado_nuevo", "usuario_actor", "fecha_cambio")
    list_filter = ("estado_nuevo",)

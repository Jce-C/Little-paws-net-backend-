"""Consulta interna de donaciones y distribuciones, sin cambios directos."""

from django.contrib import admin

from core.admin_base import SoloLecturaAdmin

from .models import DistribucionReportadaFondo, DonacionGeneral, FondoExterno


@admin.register(FondoExterno)
class FondoExternoAdmin(SoloLecturaAdmin):
    list_display = ("id_fondo_externo", "nombre")
    fields = ("id_fondo_externo", "nombre")  # No mostrar datos bancarios cifrados.
    readonly_fields = fields
    search_fields = ("nombre",)


@admin.register(DonacionGeneral)
class DonacionGeneralAdmin(SoloLecturaAdmin):
    list_display = ("id_donacion", "fondo_externo", "usuario_donante", "monto_comprometido", "estado_donacion")
    list_filter = ("estado_donacion",)


@admin.register(DistribucionReportadaFondo)
class DistribucionReportadaFondoAdmin(SoloLecturaAdmin):
    list_display = ("id_distribucion", "fondo_externo", "fundacion", "monto_reportado", "estado_distribucion")
    list_filter = ("estado_distribucion",)

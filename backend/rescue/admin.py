"""Carga supervisada de reportes y consulta de procesos de rescate."""

from decimal import Decimal

from django import forms
from django.contrib import admin
from django.db import transaction

from core.admin_base import SoloLecturaAdmin
from core.models import ValorMaestro

from .models import (
    Apadrinamiento, CasoRescate, HistorialEstadoReporte, Reporte, ReporteUbicacion,
)


class CrearReporteAdminForm(forms.ModelForm):
    descripcion = forms.CharField(max_length=5000, widget=forms.Textarea)
    latitud = forms.DecimalField(max_digits=9, decimal_places=6, min_value=Decimal("-90"), max_value=Decimal("90"))
    longitud = forms.DecimalField(max_digits=9, decimal_places=6, min_value=Decimal("-180"), max_value=Decimal("180"))

    class Meta:
        model = Reporte
        fields = ("tipo_reporte", "descripcion", "contacto_reportante")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo_reporte"].queryset = ValorMaestro.objects.filter(tipo__nombre="tipo_reporte")


@admin.register(Reporte)
class ReporteAdmin(SoloLecturaAdmin):
    list_display = ("id_reporte", "tipo_reporte", "estado_reporte", "usuario_reportante", "fecha_creacion")
    list_filter = ("estado_reporte", "tipo_reporte")
    search_fields = ("id_reporte", "descripcion")
    ordering = ("-fecha_creacion",)

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = CrearReporteAdminForm
        return super().get_form(request, obj, **kwargs)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ("tipo_reporte", "descripcion", "contacto_reportante", "latitud", "longitud")
        return (
            "id_reporte", "tipo_reporte", "estado_reporte", "usuario_reportante",
            "descripcion", "contacto_reportante", "ubicacion", "fecha_creacion", "fecha_actualizacion",
        )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return self.get_fields(request, obj)

    @admin.display(description="Ubicación")
    def ubicacion(self, obj):
        try:
            punto = obj.reporteubicacion
        except ReporteUbicacion.DoesNotExist:
            return "Sin ubicación registrada"
        return f"{punto.latitud}, {punto.longitud}"

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if change:
            return  # La edición está deshabilitada; defensa adicional.
        estado = ValorMaestro.objects.get(tipo__nombre="estado_reporte", nombre="Pendiente")
        obj.estado_reporte = estado
        obj.usuario_reportante = request.user
        super().save_model(request, obj, form, change)
        ReporteUbicacion.objects.create(
            reporte=obj, latitud=form.cleaned_data["latitud"], longitud=form.cleaned_data["longitud"],
        )
        HistorialEstadoReporte.objects.create(
            reporte=obj, estado_nuevo=estado, usuario_actor=request.user,
            observacion="Creación del reporte desde Django Admin",
        )


@admin.register(CasoRescate)
class CasoRescateAdmin(SoloLecturaAdmin):
    list_display = ("id_caso", "reporte", "fundacion", "estado_caso", "fecha_aceptacion")
    list_filter = ("estado_caso", "fundacion")


@admin.register(Apadrinamiento)
class ApadrinamientoAdmin(SoloLecturaAdmin):
    list_display = ("id_apadrinamiento", "reporte", "usuario_padrino", "monto_comprometido", "estado_apadrinamiento")
    list_filter = ("estado_apadrinamiento",)

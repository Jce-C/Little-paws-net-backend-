"""Altas de especies y razas; consulta de mascotas y expediente."""

from django.contrib import admin

from core.admin_base import CatalogoAdmin, SoloLecturaAdmin

from .models import CustodiaMascota, Especie, HistorialMedico, Mascota, Raza


@admin.register(Especie)
class EspecieAdmin(CatalogoAdmin):
    list_display = ("id_especie", "nombre")
    search_fields = ("nombre",)


@admin.register(Raza)
class RazaAdmin(CatalogoAdmin):
    list_display = ("id_raza", "nombre", "especie")
    search_fields = ("nombre", "especie__nombre")
    list_filter = ("especie",)


@admin.register(Mascota)
class MascotaAdmin(SoloLecturaAdmin):
    list_display = ("id_mascota", "nombre", "raza", "estado_mascota", "fecha_registro")
    search_fields = ("nombre", "raza__nombre")
    list_filter = ("estado_mascota", "raza__especie")


@admin.register(CustodiaMascota)
class CustodiaMascotaAdmin(SoloLecturaAdmin):
    list_display = ("id_custodia", "mascota", "fundacion", "fecha_inicio", "fecha_fin")
    list_filter = ("fundacion",)


@admin.register(HistorialMedico)
class HistorialMedicoAdmin(SoloLecturaAdmin):
    list_display = ("id_historial_medico", "mascota", "fecha_atencion", "fecha_registro")
    search_fields = ("mascota__nombre",)

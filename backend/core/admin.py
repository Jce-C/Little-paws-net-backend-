"""Catálogos editables y entidades consultables por superusuarios."""

from django.contrib import admin

from .admin_base import CatalogoAdmin, SoloLecturaAdmin
from .models import (
    Anunciante, Ciudad, Clinica, EntidadMiembro, EntidadMiembroRol,
    EntidadVerificable, Fundacion, Permiso, Rol, RolPermiso, Tienda,
    TipoMaestro, UsuarioRol, ValorMaestro, Veterinario, Zona,
)


@admin.register(TipoMaestro)
class TipoMaestroAdmin(CatalogoAdmin):
    list_display = ("id_tipo_maestro", "nombre", "activo")
    search_fields = ("nombre",)
    list_filter = ("activo",)


@admin.register(ValorMaestro)
class ValorMaestroAdmin(CatalogoAdmin):
    list_display = ("id_valor_maestro", "tipo", "nombre")
    search_fields = ("nombre", "tipo__nombre")
    list_filter = ("tipo",)


@admin.register(Ciudad)
class CiudadAdmin(CatalogoAdmin):
    list_display = ("id_ciudad", "nombre", "departamento")
    search_fields = ("nombre", "departamento")


@admin.register(Zona)
class ZonaAdmin(CatalogoAdmin):
    list_display = ("id_zona", "nombre", "ciudad")
    search_fields = ("nombre", "ciudad__nombre")
    list_filter = ("ciudad",)


@admin.register(Rol)
class RolAdmin(SoloLecturaAdmin):
    list_display = ("id_rol", "codigo", "nombre", "ambito")
    search_fields = ("codigo", "nombre")


@admin.register(Permiso)
class PermisoAdmin(SoloLecturaAdmin):
    list_display = ("id_permiso", "codigo", "descripcion")
    search_fields = ("codigo",)


@admin.register(EntidadVerificable)
class EntidadVerificableAdmin(SoloLecturaAdmin):
    list_display = ("id_entidad_verificable", "nombre", "estado_verificacion")
    search_fields = ("nombre",)
    list_filter = ("estado_verificacion",)


for modelo in (
    RolPermiso, UsuarioRol, EntidadMiembro, EntidadMiembroRol, Fundacion,
    Clinica, Veterinario, Tienda, Anunciante,
):
    admin.site.register(modelo, SoloLecturaAdmin)

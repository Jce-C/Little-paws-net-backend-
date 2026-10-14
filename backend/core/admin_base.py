"""Políticas compartidas para el panel interno de Django Admin."""

from django.contrib import admin


class SoloLecturaAdmin(admin.ModelAdmin):
    """Permite consultar, sin omitir los servicios que gestionan cambios de estado."""

    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CatalogoAdmin(admin.ModelAdmin):
    """Permite mantener catálogos simples sin borrados accidentales."""

    actions = None

    def has_delete_permission(self, request, obj=None):
        return False

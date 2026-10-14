"""Consulta de comercio sin omitir la API y sus comprobaciones de tienda."""

from django.contrib import admin

from core.admin_base import SoloLecturaAdmin

from .models import EspacioPublicitario, PedidoIniciado, Producto, TarifaPublicacion


@admin.register(Producto)
class ProductoAdmin(SoloLecturaAdmin):
    list_display = ("id_producto", "nombre", "tienda", "precio", "existencias", "estado_producto")
    search_fields = ("nombre", "tienda__entidad__nombre")
    list_filter = ("estado_producto", "tienda")


@admin.register(PedidoIniciado)
class PedidoIniciadoAdmin(SoloLecturaAdmin):
    list_display = ("id_pedido", "tienda", "usuario_cliente", "estado_pedido", "fecha_inicio")
    list_filter = ("estado_pedido", "tienda")


@admin.register(EspacioPublicitario)
class EspacioPublicitarioAdmin(SoloLecturaAdmin):
    list_display = ("id_espacio", "anunciante", "fecha_inicio", "fecha_fin")


@admin.register(TarifaPublicacion)
class TarifaPublicacionAdmin(SoloLecturaAdmin):
    list_display = ("id_tarifa", "tienda", "tipo_tarifa", "monto", "fecha_inicio", "fecha_fin")
    list_filter = ("tienda", "tipo_tarifa")

"""Rutas de tienda y publicidad (responsable: Sally Andrea)."""

from django.urls import path

from core.api import PublicidadActivaView
from .api import CatalogoView, PedidoCrearView, PedidoDetalleView


urlpatterns = [
    path("catalogo/productos/", CatalogoView.as_view(), name="catalogo_productos"),
    path("pedidos/", PedidoCrearView.as_view(), name="pedido_crear"),
    path("pedidos/<int:pedido_id>/", PedidoDetalleView.as_view(), name="pedido_detalle"),
    path("publicidad/", PublicidadActivaView.as_view(), name="publicidad_activa"),
]

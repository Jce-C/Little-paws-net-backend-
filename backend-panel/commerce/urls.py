"""Rutas de tienda y publicidad (responsable: Sally Andrea)."""

from django.urls import path

from core.api import PublicidadActivaView
from .api import CatalogoView, PedidoCrearView, PedidoDetalleView
from .photo_views import FotoProductoAdministrarView, FotoProductoConsultarView


urlpatterns = [
    path("catalogo/productos/<int:producto_id>/foto/", FotoProductoConsultarView.as_view(), name="producto_foto"),
    path("catalogo/productos/<int:producto_id>/foto-publica/", FotoProductoAdministrarView.as_view(), name="producto_foto_administrar"),
    path("catalogo/productos/", CatalogoView.as_view(), name="catalogo_productos"),
    path("pedidos/", PedidoCrearView.as_view(), name="pedido_crear"),
    path("pedidos/<int:pedido_id>/", PedidoDetalleView.as_view(), name="pedido_detalle"),
    path("publicidad/", PublicidadActivaView.as_view(), name="publicidad_activa"),
]

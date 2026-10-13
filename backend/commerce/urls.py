from django.urls import path

from .views import PedidoDetalleView, PedidoListCreateView, ProductoDetalleView, ProductoListCreateView


urlpatterns = [
    path("productos/", ProductoListCreateView.as_view(), name="producto_listar_crear"),
    path("productos/<int:producto_id>/", ProductoDetalleView.as_view(), name="producto_detalle"),
    path("pedidos/", PedidoListCreateView.as_view(), name="pedido_listar_crear"),
    path("pedidos/<int:pedido_id>/", PedidoDetalleView.as_view(), name="pedido_detalle"),
]

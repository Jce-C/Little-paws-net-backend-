from django.urls import path

from .views import (
    EspacioPublicitarioDetalleView, EspacioPublicitarioListCreateView,
    PedidoDetalleView, PedidoListCreateView, ProductoDetalleView, ProductoListCreateView,
    TarifaPublicacionDetalleView, TarifaPublicacionListCreateView,
)


urlpatterns = [
    path("productos/", ProductoListCreateView.as_view(), name="producto_listar_crear"),
    path("productos/<int:producto_id>/", ProductoDetalleView.as_view(), name="producto_detalle"),
    path("pedidos/", PedidoListCreateView.as_view(), name="pedido_listar_crear"),
    path("pedidos/<int:pedido_id>/", PedidoDetalleView.as_view(), name="pedido_detalle"),
    path("publicidad/", EspacioPublicitarioListCreateView.as_view(), name="publicidad_listar_crear"),
    path("publicidad/<int:espacio_id>/", EspacioPublicitarioDetalleView.as_view(), name="publicidad_detalle"),
    path("tarifas/", TarifaPublicacionListCreateView.as_view(), name="tarifa_listar_crear"),
    path("tarifas/<int:tarifa_id>/", TarifaPublicacionDetalleView.as_view(), name="tarifa_detalle"),
]

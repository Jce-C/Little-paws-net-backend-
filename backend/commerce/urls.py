from django.urls import path

from .views import ProductoDetalleView, ProductoListCreateView


urlpatterns = [
    path("productos/", ProductoListCreateView.as_view(), name="producto_listar_crear"),
    path("productos/<int:producto_id>/", ProductoDetalleView.as_view(), name="producto_detalle"),
]

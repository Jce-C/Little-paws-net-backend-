from django.urls import path

from .views import (
    DonacionGeneralDetalleView, DonacionGeneralListCreateView,
    FondoExternoInstruccionesView, FondoExternoListCreateView,
)


urlpatterns = [
    path("fondos/", FondoExternoListCreateView.as_view(), name="fondo_listar_crear"),
    path("fondos/<int:fondo_id>/instrucciones/", FondoExternoInstruccionesView.as_view(), name="fondo_instrucciones"),
    path("donaciones/", DonacionGeneralListCreateView.as_view(), name="donacion_listar_crear"),
    path("donaciones/<int:donacion_id>/", DonacionGeneralDetalleView.as_view(), name="donacion_detalle"),
]

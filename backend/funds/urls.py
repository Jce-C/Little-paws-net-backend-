from django.urls import path

from .views import (
    ConfirmarDistribucionView, DistribucionDetalleView, DistribucionListCreateView,
    DonacionGeneralDetalleView, DonacionGeneralListCreateView,
    FondoExternoInstruccionesView, FondoExternoListCreateView,
    ResolverDonacionView,
)


urlpatterns = [
    path("fondos/", FondoExternoListCreateView.as_view(), name="fondo_listar_crear"),
    path("fondos/<int:fondo_id>/instrucciones/", FondoExternoInstruccionesView.as_view(), name="fondo_instrucciones"),
    path("donaciones/", DonacionGeneralListCreateView.as_view(), name="donacion_listar_crear"),
    path("donaciones/<int:donacion_id>/", DonacionGeneralDetalleView.as_view(), name="donacion_detalle"),
    path("donaciones/<int:donacion_id>/resolver/", ResolverDonacionView.as_view(), name="donacion_resolver"),
    path("distribuciones/", DistribucionListCreateView.as_view(), name="distribucion_listar_crear"),
    path("distribuciones/<int:distribucion_id>/", DistribucionDetalleView.as_view(), name="distribucion_detalle"),
    path("distribuciones/<int:distribucion_id>/confirmar/", ConfirmarDistribucionView.as_view(), name="distribucion_confirmar"),
]

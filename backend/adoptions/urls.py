from django.urls import path

from .views import (
    ResolverSolicitudAdopcionView, SolicitudAdopcionDetalleView,
    SolicitudAdopcionListCreateView,
)


urlpatterns = [
    path("adopciones/", SolicitudAdopcionListCreateView.as_view(), name="adopcion_listar_crear"),
    path("adopciones/<int:solicitud_id>/", SolicitudAdopcionDetalleView.as_view(), name="adopcion_detalle"),
    path("adopciones/<int:solicitud_id>/resolver/", ResolverSolicitudAdopcionView.as_view(), name="adopcion_resolver"),
]

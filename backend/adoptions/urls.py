from django.urls import path

from .views import SolicitudAdopcionDetalleView, SolicitudAdopcionListCreateView


urlpatterns = [
    path("adopciones/", SolicitudAdopcionListCreateView.as_view(), name="adopcion_listar_crear"),
    path("adopciones/<int:solicitud_id>/", SolicitudAdopcionDetalleView.as_view(), name="adopcion_detalle"),
]

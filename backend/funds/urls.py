from django.urls import path

from .views import FondoExternoInstruccionesView, FondoExternoListCreateView


urlpatterns = [
    path("fondos/", FondoExternoListCreateView.as_view(), name="fondo_listar_crear"),
    path("fondos/<int:fondo_id>/instrucciones/", FondoExternoInstruccionesView.as_view(), name="fondo_instrucciones"),
]

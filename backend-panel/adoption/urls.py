"""Rutas del proceso de adopción (responsable: María José)."""

from django.urls import path

from .api import MascotasAdopcionView, SolicitudCrearView, SolicitudResolverView, SolicitudEvaluacionCrearView
from animals.photo_views import FotoPublicaConsultarView
from .mobile_views import MascotaFichaPublicaView, CatalogoMovilView


from .request_history import SolicitudDetalleView, MisSolicitudesView

urlpatterns = [
    path('adopcion/solicitudes/evaluacion/', SolicitudEvaluacionCrearView.as_view(), name='solicitud_evaluacion_crear'),
    path('adopcion/solicitudes/mias/', MisSolicitudesView.as_view(), name='solicitudes_mias'),
    path('adopcion/solicitudes/<int:solicitud_id>/', SolicitudDetalleView.as_view(), name='solicitud_detalle'),
    path("adopcion/mascotas/<int:mascota_id>/foto/", FotoPublicaConsultarView.as_view(), name="foto_publica_consultar"),
    path("adopcion/catalogo/", CatalogoMovilView.as_view(), name="catalogo_movil"),
    path("adopcion/mascotas/", MascotasAdopcionView.as_view(), name="mascotas_adopcion"),
    path("adopcion/mascotas/<int:mascota_id>/", MascotaFichaPublicaView.as_view(), name="mascota_ficha_publica"),
    path("adopcion/solicitudes/", SolicitudCrearView.as_view(), name="solicitud_adopcion_crear"),
    path("adopcion/solicitudes/<int:solicitud_id>/resolver/", SolicitudResolverView.as_view(), name="solicitud_adopcion_resolver"),
]

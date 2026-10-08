from django.urls import path

from .views import (
    AceptarReporteView, CasoDetalleView, CerrarCasoView, GestionAnonimaView,
    ReporteCrearView, ReporteDetalleView,
)


urlpatterns = [
    path("reportes/", ReporteCrearView.as_view(), name="reporte_crear"),
    path("reportes/<int:reporte_id>/", ReporteDetalleView.as_view(), name="reporte_detalle"),
    path("reportes/<int:reporte_id>/gestion-anonima/", GestionAnonimaView.as_view(), name="reporte_gestion_anonima"),
    path("reportes/<int:reporte_id>/aceptar/", AceptarReporteView.as_view(), name="reporte_aceptar"),
    path("casos/<int:caso_id>/", CasoDetalleView.as_view(), name="caso_detalle"),
    path("casos/<int:caso_id>/cerrar/", CerrarCasoView.as_view(), name="caso_cerrar"),
]

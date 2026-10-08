from django.urls import path

from .views import (
    AceptarReporteView, CasoDetalleView, CerrarCasoView, GestionAnonimaView,
    ReporteCrearView, ReporteDetalleView,
)
from .sponsorship_views import (
    CompromisoView, ConfirmacionView, CuentaCrearView, CuentaRevelarView, DeclaracionView,
)


urlpatterns = [
    path("reportes/", ReporteCrearView.as_view(), name="reporte_crear"),
    path("reportes/<int:reporte_id>/", ReporteDetalleView.as_view(), name="reporte_detalle"),
    path("reportes/<int:reporte_id>/gestion-anonima/", GestionAnonimaView.as_view(), name="reporte_gestion_anonima"),
    path("reportes/<int:reporte_id>/aceptar/", AceptarReporteView.as_view(), name="reporte_aceptar"),
    path("casos/<int:caso_id>/", CasoDetalleView.as_view(), name="caso_detalle"),
    path("casos/<int:caso_id>/cerrar/", CerrarCasoView.as_view(), name="caso_cerrar"),
    path("apadrinamientos/", CompromisoView.as_view(), name="apadrinamiento_crear"),
    path("apadrinamientos/<int:apadrinamiento_id>/cuenta/", CuentaRevelarView.as_view(), name="apadrinamiento_cuenta"),
    path("apadrinamientos/<int:apadrinamiento_id>/declaraciones/", DeclaracionView.as_view(), name="apadrinamiento_declarar"),
    path("apadrinamientos/<int:apadrinamiento_id>/confirmaciones/", ConfirmacionView.as_view(), name="apadrinamiento_confirmar"),
    path("fundaciones/<int:fundacion_id>/cuentas/", CuentaCrearView.as_view(), name="fundacion_cuenta_crear"),
]

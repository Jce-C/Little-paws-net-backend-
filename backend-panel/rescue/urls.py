"""Rutas de reporte, rescate y apadrinamiento."""

from django.urls import path

from .sponsorship_views import (
    MisCompromisosView, CompromisoView, ConfirmacionView, CuentaCrearView, CuentaRevelarView, DeclaracionView,
)
from .mobile_views import MisReportesView, OpcionesReporteView, ReportesPublicosPaginadosView
from .views import AceptarReporteView, CasoDetalleView, GestionAnonimaView, ReporteCrearView


from .photo_views import FotoReporteView

urlpatterns = [
    path('reportes/<int:reporte_id>/foto/', FotoReporteView.as_view(), name='reporte_foto'),
    path("reportes/publicos/", ReportesPublicosPaginadosView.as_view(), name="reportes_publicos_paginados"),
    path("reportes/opciones/", OpcionesReporteView.as_view(), name="reporte_opciones"),
    path("reportes/mios/", MisReportesView.as_view(), name="reportes_mios"),
    path("reportes/", ReporteCrearView.as_view(), name="reporte_crear"),
    path("reportes/<int:reporte_id>/gestion-anonima/", GestionAnonimaView.as_view(), name="reporte_gestion_anonima"),
    path("reportes/<int:reporte_id>/aceptar/", AceptarReporteView.as_view(), name="reporte_aceptar"),
    path("casos/<int:caso_id>/", CasoDetalleView.as_view(), name="caso_detalle"),
    path("apadrinamientos/mios/", MisCompromisosView.as_view(), name="mis_compromisos"),
    path("apadrinamientos/", CompromisoView.as_view(), name="apadrinamiento_crear"),
    path("apadrinamientos/<int:apadrinamiento_id>/cuenta/", CuentaRevelarView.as_view(), name="apadrinamiento_cuenta"),
    path("apadrinamientos/<int:apadrinamiento_id>/declaraciones/", DeclaracionView.as_view(), name="apadrinamiento_declarar"),
    path("apadrinamientos/<int:apadrinamiento_id>/confirmaciones/", ConfirmacionView.as_view(), name="apadrinamiento_confirmar"),
    path("fundaciones/<int:fundacion_id>/cuentas/", CuentaCrearView.as_view(), name="fundacion_cuenta_crear"),
]

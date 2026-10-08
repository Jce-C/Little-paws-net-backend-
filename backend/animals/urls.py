from django.urls import path

from .views import (
    AtencionExternaView, AtencionView, AutorizacionView, CustodiaView,
    ExpedienteConsultarView, MascotaCasoView, QRView,
)


urlpatterns = [
    path("casos/<int:caso_id>/mascota/", MascotaCasoView.as_view(), name="caso_mascota_crear"),
    path("casos/<int:caso_id>/custodia/", CustodiaView.as_view(), name="custodia_registrar"),
    path("expedientes/<int:mascota_id>/autorizaciones/", AutorizacionView.as_view(), name="expediente_autorizar"),
    path("expedientes/<int:mascota_id>/qr/", QRView.as_view(), name="expediente_qr"),
    path("expedientes/<int:mascota_id>/consultar/", ExpedienteConsultarView.as_view(), name="expediente_consultar"),
    path("expedientes/<int:mascota_id>/registros/", AtencionView.as_view(), name="expediente_registrar"),
    path("expedientes/<int:mascota_id>/registros-externos/", AtencionExternaView.as_view(), name="expediente_registrar_externo"),
]

"""Rutas del expediente veterinario."""

from django.urls import path

from .views import AtencionCrearView, AutorizarView, QRConsultarView, QRCrearView
from .mobile_views import MisMascotasView
from .photo_views import FotoPublicaAdministrarView, FotoGaleriaAdministrarView, FotoPublicaConsultarView
from .public_presentation import PresentacionAdministrarView


from .personal_views import MascotaPersonalCrearView, MascotaPersonalDetalleView

urlpatterns = [
    path('mascotas/personales/<int:mascota_id>/', MascotaPersonalDetalleView.as_view(), name='mascota_personal_detalle'),
    path('mascotas/personales/', MascotaPersonalCrearView.as_view(), name='mascota_personal_crear'),
    path("mascotas/<int:mascota_id>/presentacion-publica/", PresentacionAdministrarView.as_view(), name="presentacion_publica"),
    path("mascotas/<int:mascota_id>/galeria/", FotoGaleriaAdministrarView.as_view(), name="galeria_publicar"),
    path("mascotas/<int:mascota_id>/galeria/<int:foto_id>/", FotoGaleriaAdministrarView.as_view(), name="galeria_retirar"),
    path("adopcion/mascotas/<int:mascota_id>/fotos/<int:foto_id>/", FotoPublicaConsultarView.as_view(), name="galeria_foto"),
    path("mascotas/<int:mascota_id>/foto-publica/", FotoPublicaAdministrarView.as_view(), name="foto_publica_administrar"),
    path("mascotas/mias/", MisMascotasView.as_view(), name="mascotas_mias"),
    path("mascotas/<int:mascota_id>/autorizaciones/", AutorizarView.as_view(), name="expediente_autorizar"),
    path("mascotas/<int:mascota_id>/qr/", QRCrearView.as_view(), name="qr_crear"),
    path("qr/<str:token>/", QRConsultarView.as_view(), name="qr_consultar"),
    path("qr/<str:token>/atenciones/", AtencionCrearView.as_view(), name="atencion_crear"),
]

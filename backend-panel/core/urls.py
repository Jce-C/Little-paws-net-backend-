"""Rutas compartidas de catálogos y notificaciones."""

from django.urls import path

from .api import CatalogosView, LeerNotificacionView, MisNotificacionesView
from .mobile_directory import OrganizacionesPublicasView
from .public_profiles import PerfilAdministrarView
from .avatar_views import AvatarPerfilConsultarView
from .logo_views import LogoEntidadAdministrarView, LogoEntidadConsultarView
from .help_programs import ProgramaAdministrarView
from .community_api import PublicacionesView, ComentariosView, ReaccionView, RetirarPublicacionView, InteresesAyudaView, MisOrganizacionesAyudaView, OrganizacionAyudaView


urlpatterns = [
    path("comunidad/perfiles/<uuid:public_id>/foto/", AvatarPerfilConsultarView.as_view(), name="comunidad_foto_perfil"),
    path("red/organizaciones/<int:entidad_id>/logo-publico/", LogoEntidadAdministrarView.as_view(), name="organizacion_logo_administrar"),
    path("red/organizaciones/<int:entidad_id>/logo/", LogoEntidadConsultarView.as_view(), name="organizacion_logo_publico"),
    path("ayudas/organizaciones/<int:fundacion_id>/programa/", ProgramaAdministrarView.as_view(), name="ayudas_programa"),
    path("red/organizaciones/<int:entidad_id>/perfil/", PerfilAdministrarView.as_view(), name="organizacion_perfil"),
    path("comunidad/publicaciones/", PublicacionesView.as_view(), name="comunidad_publicaciones"),
    path("comunidad/publicaciones/<int:publicacion_id>/comentarios/", ComentariosView.as_view(), name="comunidad_comentarios"),
    path("comunidad/publicaciones/<int:publicacion_id>/reaccion/", ReaccionView.as_view(), name="comunidad_reaccion"),
    path("comunidad/publicaciones/<int:publicacion_id>/retirar/", RetirarPublicacionView.as_view(), name="comunidad_retirar"),
    path("ayudas/intereses/", InteresesAyudaView.as_view(), name="ayudas_intereses"),
    path("ayudas/organizaciones/", MisOrganizacionesAyudaView.as_view(), name="ayudas_organizaciones"),
    path("ayudas/organizaciones/<int:fundacion_id>/", OrganizacionAyudaView.as_view(), name="ayudas_organizacion"),
    path("red/organizaciones/", OrganizacionesPublicasView.as_view(), name="organizaciones_publicas"),
    path("catalogos/", CatalogosView.as_view(), name="catalogos"),
    path("notificaciones/", MisNotificacionesView.as_view(), name="mis_notificaciones"),
    path("notificaciones/<int:notificacion_id>/leer/", LeerNotificacionView.as_view(), name="notificacion_leer"),
]

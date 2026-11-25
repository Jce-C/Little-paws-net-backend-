from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views
from .rbac_api import ExcepcionesPermisoView
from . import negocio_api as negocio

app_name = "seguridad"
router = SimpleRouter()
router.register("usuarios", views.UsuariosViewSet)
router.register("recursos", views.RecursosViewSet)
router.register("permisos", views.PermisosViewSet)
router.register("roles", views.RolesViewSet)

from .asignaciones_api import RolesPersonaView
from .catalogos_api import CatalogoView
from .bajas_api import BajaView
urlpatterns = [
    path('usuarios/<int:usuario_id>/asignaciones-roles/',RolesPersonaView.as_view()),
    path('casos/<int:pk>/mascota/',negocio.MascotaRescateView.as_view()),
    path('mascotas-administrar/<int:pk>/disponibilidad/',negocio.PublicarAdopcionView.as_view()),
    path('catalogos/<slug:tipo>/',CatalogoView.as_view()),
    path('catalogos/<slug:tipo>/<int:pk>/',CatalogoView.as_view()),
    path('organizaciones/<int:pk>/cobertura/',negocio.CoberturaView.as_view()),
    path('administracion/<slug:tipo>/<int:pk>/baja/',BajaView.as_view()),
    path('organizaciones/',negocio.OrganizacionesView.as_view()),
    path('organizaciones/<int:pk>/',negocio.OrganizacionDetalleView.as_view()),
    path('seguimientos/<int:pk>/',negocio.SeguimientoView.as_view()),
    path('fondos-administrar/<int:pk>/',negocio.FondosAdministrarView.as_view()),
    path('fondos-administrar/',negocio.FondosAdministrarView.as_view()),
    path('mascotas-administrar/<int:pk>/',negocio.MascotaAdministrarView.as_view()),
    path('mascotas-administrar/',negocio.MascotaAdministrarView.as_view()),
    path('usuarios/<int:usuario_id>/excepciones/',ExcepcionesPermisoView.as_view()),
    path("operaciones/", include("seguridad.flujos_urls")),
    path("", include(router.urls)),
    path("mis-accesos/", views.EfectivosView.as_view(), name="mis-accesos"),
    path("comprobar/", views.ComprobarView.as_view(), name="comprobar"),
    path("usuarios/<int:usuario_id>/roles-globales/", views.RolGlobalView.as_view()),
    path("entidades/", views.EntidadesView.as_view()),
    path("entidades/<int:entidad_id>/miembros/", views.MiembrosView.as_view()),
    path("entidades/<int:entidad_id>/roles/", views.RolEntidadView.as_view()),
    path("entidades/<int:entidad_id>/principal/", views.PrincipalView.as_view()),
    path("entidades/<int:entidad_id>/transferencias/", views.TransferirView.as_view()),
    path("transferencias/<int:transferencia_id>/resolver/", views.ResolverTransferenciaView.as_view()),
    path("colas/<slug:recurso>/", views.ColaView.as_view()),
    path("asignaciones/<slug:recurso>/<int:objeto_id>/tomar/", views.TomarView.as_view()),
    path("asignaciones/<slug:recurso>/<int:objeto_id>/devolver/", views.DevolverView.as_view()),
    path("fondos/<int:fondo_id>/asignar/", views.AsignarFondoView.as_view()),
    path("auditoria/", views.AuditoriaView.as_view()),
]

from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = "seguridad"
router = SimpleRouter()
router.register("usuarios", views.UsuariosViewSet)
router.register("recursos", views.RecursosViewSet)
router.register("permisos", views.PermisosViewSet)
router.register("roles", views.RolesViewSet)

urlpatterns = [
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

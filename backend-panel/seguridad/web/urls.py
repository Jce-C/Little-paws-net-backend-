from django.urls import path
from . import views
from .preferencias import guardar
from .administracion import seguridad
from .estado import estado
from .dashboard import configuracion,perfil,auditoria
from .negocio import area
from .foto_mascota import fotografia
from .foto_producto import fotografia as fotografia_producto
from .perfil_publico import perfil_publico
from .logo_entidad import logo_publico
from .presentacion_mascota import presentacion
from .programa_ayuda import programa
from .usuarios import usuarios
from seguridad.realtime import eventos

app_name = "panel"
from .catalogos import catalogos
from .bajas import baja
from .acciones import acciones
urlpatterns = [
    path("organizaciones/<int:entidad_id>/logo/", logo_publico, name="logo_entidad"),
    path("ayudas/<int:fundacion_id>/programa/", programa, name="programa_ayuda"),
    path("mascotas/<int:mascota_id>/presentacion/", presentacion, name="presentacion_mascota"),
    path("organizaciones/<int:entidad_id>/perfil-publico/", perfil_publico, name="perfil_publico"),
    path("productos/<int:producto_id>/fotografia/", fotografia_producto, name="foto_producto"),
    path("mascotas/<int:mascota_id>/fotografia/", fotografia, name="foto_mascota"),
    path('catalogos/',catalogos,name='catalogos'),
    path('bajas/<slug:tipo>/<int:pk>/',baja,name='baja'),
    path('acciones/',acciones,name='acciones'),
    path('usuarios/',usuarios,name='usuarios'),
    path('areas/<slug:codigo>/',area,name='area'),
    path('configuracion/',configuracion,name='configuracion'),
    path('perfil-visual/',perfil,name='perfil_visual'),
    path('auditoria/',auditoria,name='auditoria'),
    path('estado/',estado,name='estado'),
    path('eventos/',eventos,name='eventos'),
    path("seguridad/", seguridad, name="seguridad"),
    path("preferencias/", guardar, name="preferencias"),
    path("login/", views.iniciar, name="login"),
    path("logout/", views.salir, name="logout"),
    path("cambiar-clave/", views.cambiar_clave, name="cambiar_clave"),
    path("organizacion/", views.seleccionar, name="organizacion"),
    path("modulos/<slug:codigo>/", views.modulo, name="modulo"),
    path("", views.inicio, name="inicio"),
]

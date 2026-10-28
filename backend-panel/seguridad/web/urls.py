from django.urls import path
from . import views

app_name = "panel"
urlpatterns = [
    path("login/", views.iniciar, name="login"),
    path("logout/", views.salir, name="logout"),
    path("cambiar-clave/", views.cambiar_clave, name="cambiar_clave"),
    path("organizacion/", views.seleccionar, name="organizacion"),
    path("modulos/<slug:codigo>/", views.modulo, name="modulo"),
    path("", views.inicio, name="inicio"),
]

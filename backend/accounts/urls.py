"""Rutas de autenticación."""

from django.urls import path

from .token_views import TokenObtainLimitadoView, TokenRefreshLimitadoView, TokenRevocarLimitadoView
from .views import PerfilView, RegistroView


urlpatterns = [
    path("registro/", RegistroView.as_view(), name="registro"),
    path("token/", TokenObtainLimitadoView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshLimitadoView.as_view(), name="token_refresh"),
    path("token/revoke/", TokenRevocarLimitadoView.as_view(), name="token_revoke"),
    path("perfil/", PerfilView.as_view(), name="perfil"),
]

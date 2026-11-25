"""Límite de intentos para los endpoints de autenticación."""

from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from seguridad.web.acceso import ip_cliente


class LimiteDesdeEdge(ScopedRateThrottle):
    def get_ident(self, request):
        return ip_cliente(request)


class TokenSinClaveTemporalSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        if user.debe_cambiar_clave:
            raise AuthenticationFailed("Cambia tu contraseña temporal desde el panel.")
        return super().get_token(user)


class TokenObtainLimitadoView(TokenObtainPairView):
    serializer_class = TokenSinClaveTemporalSerializer
    throttle_classes = [LimiteDesdeEdge]
    throttle_scope = "auth"


class TokenRefreshLimitadoView(TokenRefreshView):
    throttle_classes = [LimiteDesdeEdge]
    throttle_scope = "auth"


class TokenRevocarLimitadoView(TokenBlacklistView):
    throttle_classes = [LimiteDesdeEdge]
    throttle_scope = "auth"

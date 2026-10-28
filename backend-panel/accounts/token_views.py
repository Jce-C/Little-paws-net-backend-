"""Límite de intentos para los endpoints de autenticación."""

from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView


class TokenObtainLimitadoView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class TokenRefreshLimitadoView(TokenRefreshView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class TokenRevocarLimitadoView(TokenBlacklistView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

"""Vistas JSON de registro y perfil."""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.db import transaction

from .serializers import PerfilPropioSerializer, RegistroSerializer
from .models import Usuario


class RegistroView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        return Response({"id_usuario": usuario.pk, "email": usuario.email}, status=status.HTTP_201_CREATED)


class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response

    def get(self, request):
        return self.respuesta(request.user)

    @transaction.atomic
    def patch(self, request):
        serializer = PerfilPropioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = Usuario.objects.select_for_update().get(pk=request.user.pk)
        if not usuario.is_active:
            raise PermissionDenied("La cuenta ya no está activa.")
        cambios = []
        for field, value in serializer.validated_data.items():
            if getattr(usuario, field) != value:
                setattr(usuario, field, value)
                cambios.append(field)
        if cambios:
            usuario.save(update_fields=cambios)
            from seguridad.servicios import auditar
            auditar(usuario, "perfil.actualizar", "usuarios", usuario.pk, campos=sorted(cambios))
        return self.respuesta(usuario)

    @staticmethod
    def respuesta(usuario):
        return Response({
            "id_usuario": usuario.pk,
            "reintentos_seguros": True,
            "evaluacion_adopcion": True,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "telefono": usuario.telefono,
        })

from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.throttling import UserRateThrottle
from seguridad.serializers import EntradaEstricta
from .models import LogoPublicoEntidad
from . import public_logos as photos


class LogoEntrada(EntradaEstricta, serializers.Serializer):
    archivo = serializers.FileField()
    confirmar_publicacion = serializers.BooleanField()


class LogoEntidadThrottle(UserRateThrottle):
    scope = 'organization_logo_upload'
    rate = '10/min'


class SinCache(APIView):
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class LogoEntidadAdministrarView(SinCache):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_throttles(self):
        return [LogoEntidadThrottle()] if self.request.method == 'POST' else []

    def post(self, request, entidad_id):
        entrada = LogoEntrada(data=request.data)
        entrada.is_valid(raise_exception=True)
        photo = photos.publicar(request.user, entidad_id, entrada.validated_data['archivo'], entrada.validated_data['confirmar_publicacion'])
        return Response({'logo': photos.descriptor(photo.entidad)}, status=201)

    def delete(self, request, entidad_id):
        photos.retirar(request.user, entidad_id)
        return Response(status=204)


class LogoEntidadConsultarView(SinCache):
    permission_classes = [AllowAny]

    def get(self, request, entidad_id):
        entity = get_object_or_404(photos.disponibles(), pk=entidad_id)
        photo = get_object_or_404(LogoPublicoEntidad, entidad=entity, publicada=True)
        path = photos.ruta(photo.clave)
        try:
            with path.open('rb') as stream:
                content = stream.read(photos.MAX_LOGO + 1)
            if len(content) != photo.tamano_bytes or len(content) > photos.MAX_LOGO:
                raise NotFound(_('Logo no disponible.'))
        except FileNotFoundError as exc:
            raise NotFound(_('Logo no disponible.')) from exc
        except OSError as exc:
            raise photos.StorageUnavailable() from exc
        response = HttpResponse(content, content_type='image/webp')
        response['Content-Length'] = str(len(content))
        response['Content-Disposition'] = f'inline; filename="organizacion-{entidad_id}.webp"'
        response['Content-Security-Policy'] = "default-src 'none'; sandbox"
        return response

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
from .models import FotoPublicaPerfil
from . import public_avatars as photos


class AvatarEntrada(EntradaEstricta, serializers.Serializer):
    archivo = serializers.FileField()
    confirmar_publicacion = serializers.BooleanField()


class AvatarPerfilThrottle(UserRateThrottle):
    scope = 'profile_photo_upload'
    rate = '10/min'


class SinCache(APIView):
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class AvatarPerfilAdministrarView(SinCache):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_throttles(self):
        return [AvatarPerfilThrottle()] if self.request.method == 'POST' else []

    def get(self, request):
        user = photos.propietario(request.user)
        return Response({'foto_publica': photos.descriptor(user)})

    def post(self, request):
        entrada = AvatarEntrada(data=request.data)
        entrada.is_valid(raise_exception=True)
        photo = photos.publicar(request.user, entrada.validated_data['archivo'], entrada.validated_data['confirmar_publicacion'])
        return Response({'foto_publica': photos.descriptor(photo.usuario)}, status=201)

    def delete(self, request):
        photos.retirar(request.user)
        return Response(status=204)


class AvatarPerfilConsultarView(SinCache):
    permission_classes = [AllowAny]

    def get(self, request, public_id):
        photo = get_object_or_404(FotoPublicaPerfil, public_id=public_id, publicada=True, usuario__is_active=True)
        path = photos.ruta(photo.clave)
        try:
            with path.open('rb') as stream:
                content = stream.read(photos.MAX_AVATAR + 1)
            if len(content) != photo.tamano_bytes or len(content) > photos.MAX_AVATAR:
                raise NotFound(_('Foto de perfil no disponible.'))
        except FileNotFoundError as exc:
            raise NotFound(_('Foto de perfil no disponible.')) from exc
        except OSError as exc:
            raise photos.StorageUnavailable() from exc
        response = HttpResponse(content, content_type='image/webp')
        response['Content-Length'] = str(len(content))
        response['Content-Disposition'] = f'inline; filename="perfil.webp"'
        response['Content-Security-Policy'] = "default-src 'none'; sandbox"
        return response

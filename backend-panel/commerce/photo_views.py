from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.throttling import UserRateThrottle
from seguridad.serializers import EntradaEstricta
from .models import FotoPublicaProducto
from . import public_photos as photos


class FotoEntrada(EntradaEstricta, serializers.Serializer):
    archivo = serializers.FileField()
    confirmar_publicacion = serializers.BooleanField()


class FotoProductoThrottle(UserRateThrottle):
    scope = 'product_photo_upload'
    rate = '10/min'


class SinCache(APIView):
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class FotoProductoAdministrarView(SinCache):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_throttles(self):
        return [FotoProductoThrottle()] if self.request.method == 'POST' else []

    def post(self, request, producto_id):
        entrada = FotoEntrada(data=request.data)
        entrada.is_valid(raise_exception=True)
        photo = photos.publicar(request.user, producto_id, entrada.validated_data['archivo'], entrada.validated_data['confirmar_publicacion'])
        return Response({'foto_url': f'/api/catalogo/productos/{producto_id}/foto/',
                         'ancho': photo.ancho, 'alto': photo.alto, 'bytes': photo.tamano_bytes}, status=201)

    def delete(self, request, producto_id):
        photos.retirar(request.user, producto_id)
        return Response(status=204)


class FotoProductoConsultarView(SinCache):
    permission_classes = [AllowAny]

    def get(self, request, producto_id):
        product = get_object_or_404(photos.disponibles(), pk=producto_id)
        photo = get_object_or_404(FotoPublicaProducto, producto=product, tienda_id=product.tienda_id, publicada=True)
        path = photos.ruta(photo.clave)
        try:
            with path.open('rb') as stream:
                content = stream.read(photos.MAX_OUTPUT + 1)
            if len(content) != photo.tamano_bytes or len(content) > photos.MAX_OUTPUT:
                raise NotFound('Fotografía no disponible.')
        except FileNotFoundError as exc:
            raise NotFound('Fotografía no disponible.') from exc
        except OSError as exc:
            raise photos.StorageUnavailable() from exc
        response = HttpResponse(content, content_type='image/webp')
        response['Content-Length'] = str(len(content))
        response['Content-Disposition'] = f'inline; filename="producto-{producto_id}.webp"'
        response['Content-Security-Policy'] = "default-src 'none'; sandbox"
        return response

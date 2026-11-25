from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from seguridad.serializers import EntradaEstricta
from adoption.consultas import disponibles_adopcion
from .models import CustodiaMascota, FotoPublicaMascota, FotoGaleriaMascota
from . import public_photos


class FotoEntrada(EntradaEstricta, serializers.Serializer):
    archivo = serializers.FileField()
    confirmar_publicacion = serializers.BooleanField()


class FotoPublicaThrottle(UserRateThrottle):
    scope = "pet_photo_upload"
    rate = "10/min"


class FotoPublicaAdministrarView(APIView):
    adicional = False
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_throttles(self):
        return [FotoPublicaThrottle()] if self.request.method == "POST" else []

    def post(self, request, mascota_id):
        serializer = FotoEntrada(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        photo = public_photos.publicar(request.user, mascota_id, data["archivo"], data["confirmar_publicacion"], adicional=self.adicional)
        url = f"/api/adopcion/mascotas/{mascota_id}/fotos/{photo.pk}/" if self.adicional else f"/api/adopcion/mascotas/{mascota_id}/foto/"
        payload = {"foto_url": url, "ancho": photo.ancho, "alto": photo.alto, "bytes": photo.tamano_bytes}
        if self.adicional:
            payload["id_foto"] = photo.pk
        response = Response(payload, status=201)
        response["Cache-Control"] = "no-store"
        return response

    def delete(self, request, mascota_id):
        public_photos.retirar(request.user, mascota_id)
        return Response(status=204)


class FotoPublicaConsultarView(APIView):
    permission_classes = [AllowAny]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response

    def get(self, request, mascota_id, foto_id=None):
        get_object_or_404(disponibles_adopcion(), pk=mascota_id)
        custody = get_object_or_404(CustodiaMascota, mascota_id=mascota_id, fecha_fin__isnull=True)
        source = FotoGaleriaMascota.objects.filter(pk=foto_id) if foto_id is not None else FotoPublicaMascota.objects.all()
        photo = get_object_or_404(source, mascota_id=mascota_id, fundacion_id=custody.fundacion_id, publicada=True)
        path = public_photos.ruta(photo.clave)
        try:
            with path.open("rb") as stream:
                content = stream.read(public_photos.MAX_OUTPUT + 1)
            if len(content) != photo.tamano_bytes or len(content) > public_photos.MAX_OUTPUT:
                raise NotFound("Fotografía no disponible.")
        except FileNotFoundError as exc:
            raise NotFound("Fotografía no disponible.") from exc
        except OSError as exc:
            raise public_photos.StorageUnavailable() from exc
        response = HttpResponse(content, content_type="image/webp")
        response["Content-Length"] = str(len(content))
        response["Content-Disposition"] = f'inline; filename="mascota-{mascota_id}.webp"'
        response["Cache-Control"] = "no-store"
        response["X-Content-Type-Options"] = "nosniff"
        response["Content-Security-Policy"] = "default-src 'none'; sandbox"
        return response


class FotoGaleriaAdministrarView(FotoPublicaAdministrarView):
    adicional = True

    def post(self, request, mascota_id, foto_id=None):
        if foto_id is not None:
            return Response({"detalle": "Agrega fotografías desde la galería de la mascota."}, status=405)
        return super().post(request, mascota_id)

    def delete(self, request, mascota_id, foto_id=None):
        if foto_id is None:
            return Response({"detalle": "Selecciona la fotografía que deseas retirar."}, status=400)
        public_photos.retirar(request.user, mascota_id, foto_id=foto_id)
        return Response(status=204)

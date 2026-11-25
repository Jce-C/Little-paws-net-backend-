"""Publicación editorial de adopción, ligada a la custodia que la autorizó."""
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from seguridad.autorizacion import invalidar
from seguridad.servicios import auditar, bloqueo_seguridad
from seguridad.serializers import EntradaEstricta
from adoption.consultas import disponibles_adopcion
from .public_photos import custodia_autorizada
from .models import PresentacionPublicaMascota

CAMPOS = ('descripcion', 'cuidados', 'espacio', 'publicada')


class PresentacionEntrada(EntradaEstricta, serializers.Serializer):
    descripcion = serializers.CharField(max_length=1000, allow_blank=True, default='')
    cuidados = serializers.CharField(max_length=2000, allow_blank=True, default='')
    espacio = serializers.CharField(max_length=600, allow_blank=True, default='')
    publicada = serializers.BooleanField()
    confirmar_publicacion = serializers.BooleanField(default=False)

    def validate(self, values):
        if values['publicada']:
            if not values['confirmar_publicacion']:
                raise serializers.ValidationError(_('Confirma que estos textos están autorizados para publicación y no contienen información privada.'))
            if not values['descripcion']:
                raise serializers.ValidationError(_('Escribe una descripción antes de publicar.'))
        return values


def datos(profile):
    return {name: getattr(profile, name) for name in CAMPOS}


def descriptor(pet, fundacion_id):
    profile = getattr(pet, 'presentacion_publica', None)
    if profile is None or not profile.publicada or profile.fundacion_id != fundacion_id:
        return None
    return {name: getattr(profile, name) for name in CAMPOS if name != 'publicada'}


@transaction.atomic
def guardar(actor, mascota_id, values):
    bloqueo_seguridad()
    invalidar()
    pet, custody = custodia_autorizada(actor, mascota_id)
    serializer = PresentacionEntrada(data=values)
    serializer.is_valid(raise_exception=True)
    clean = serializer.validated_data
    if clean['publicada'] and not disponibles_adopcion().filter(pk=pet.pk).exists():
        raise ValidationError(_('La mascota debe estar disponible para adopción antes de publicar su presentación.'))
    previous = PresentacionPublicaMascota.objects.filter(mascota=pet, fundacion=custody.fundacion).first()
    before = datos(previous) if previous else {}
    profile, _created = PresentacionPublicaMascota.objects.update_or_create(mascota=pet, defaults={
        **{name: clean[name] for name in CAMPOS}, 'fundacion': custody.fundacion, 'editor': actor,
    })
    auditar(actor, 'mascotas.presentacion_publica', 'mascotas', pet.pk, custody.fundacion_id,
            motivo='Publicación editorial autorizada' if profile.publicada else 'Presentación guardada sin publicar',
            anterior=before, nuevo=datos(profile))
    return profile


class PresentacionAdministrarView(APIView):
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        return response

    def get(self, request, mascota_id):
        pet, custody = custodia_autorizada(request.user, mascota_id, bloquear=False)
        profile = PresentacionPublicaMascota.objects.filter(mascota=pet, fundacion=custody.fundacion).first()
        return Response(datos(profile) if profile else {'descripcion': '', 'cuidados': '', 'espacio': '', 'publicada': False})

    def put(self, request, mascota_id):
        return Response(datos(guardar(request.user, mascota_id, request.data)))

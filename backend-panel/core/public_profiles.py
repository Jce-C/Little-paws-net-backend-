"""Ficha pública editorial: el mismo servicio se usa en API y panel."""
from urllib.parse import urlsplit
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from seguridad.autorizacion import exigir, invalidar
from seguridad.servicios import auditar, bloqueo_seguridad
from seguridad.serializers import EntradaEstricta
from seguridad.models import BajaAdministrativa
from .models import EntidadVerificable, PerfilPublicoEntidad, Fundacion, Clinica, Tienda

CAMPOS = ('descripcion', 'servicios', 'telefono', 'correo', 'sitio_web', 'publicada')


class PerfilEntrada(EntradaEstricta, serializers.Serializer):
    descripcion = serializers.CharField(max_length=2000, allow_blank=True, default='')
    servicios = serializers.CharField(max_length=1000, allow_blank=True, default='')
    telefono = serializers.RegexField(r'^\+?[0-9 ()-]{5,32}$', max_length=32, allow_blank=True, default='')
    correo = serializers.EmailField(max_length=254, allow_blank=True, default='')
    sitio_web = serializers.URLField(max_length=200, allow_blank=True, default='')
    publicada = serializers.BooleanField()
    confirmar_publicacion = serializers.BooleanField(default=False)

    def validate_sitio_web(self, value):
        if value:
            url = urlsplit(value)
            if url.scheme != 'https' or not url.hostname or url.username or url.password:
                raise serializers.ValidationError('Usa una dirección HTTPS pública sin credenciales.')
        return value

    def validate(self, attrs):
        if attrs['publicada'] and not attrs['confirmar_publicacion']:
            raise serializers.ValidationError('Confirma la autorización para publicar estos datos de contacto y servicios.')
        if attrs['publicada'] and not attrs['descripcion']:
            raise serializers.ValidationError('Escribe una descripción antes de publicar la ficha.')
        return attrs


def autorizado(actor, entidad_id):
    exigir(actor, 'entidades.editar')
    return get_object_or_404(EntidadVerificable, pk=entidad_id)


def datos(profile):
    return {name: getattr(profile, name) for name in CAMPOS}


def descriptor(entity):
    profile = getattr(entity, 'perfil_publico', None)
    if profile is None or not profile.publicada:
        return None
    return {name: getattr(profile, name) for name in CAMPOS if name != 'publicada'}


@transaction.atomic
def guardar(actor, entidad_id, values):
    bloqueo_seguridad()
    invalidar()
    autorizado(actor, entidad_id)
    entity = get_object_or_404(EntidadVerificable.objects.select_for_update().select_related('estado_verificacion'), pk=entidad_id)
    if BajaAdministrativa.objects.filter(tipo='entidades', objeto_id=entity.pk, activo=False).exists():
        raise ValidationError('Restaura la organización antes de editar su ficha pública.')
    if not any(model.objects.filter(pk=entity.pk).exists() for model in (Fundacion, Clinica, Tienda)):
        raise ValidationError('La organización debe ser una fundación, clínica o tienda registrada.')
    entrada = PerfilEntrada(data=values)
    entrada.is_valid(raise_exception=True)
    clean = entrada.validated_data
    if clean['publicada'] and entity.estado_verificacion.nombre != 'Verificada':
        raise ValidationError('La organización debe estar verificada antes de publicar su ficha.')
    previous = PerfilPublicoEntidad.objects.filter(entidad=entity).first()
    before = datos(previous) if previous else {}
    profile, _ = PerfilPublicoEntidad.objects.update_or_create(entidad=entity, defaults={
        **{name: clean[name] for name in CAMPOS}, 'editor': actor,
    })
    auditar(actor, 'entidad.perfil_publico', 'entidades', entity.pk, entity.pk,
            motivo='Autorización explícita de ficha pública' if profile.publicada else 'Guardado de ficha no publicada',
            anterior=before, nuevo=datos(profile))
    return profile


class PerfilAdministrarView(APIView):
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        return response

    def get(self, request, entidad_id):
        entity = autorizado(request.user, entidad_id)
        profile = PerfilPublicoEntidad.objects.filter(entidad=entity).first()
        return Response(datos(profile) if profile else {**{name: '' for name in CAMPOS if name != 'publicada'}, 'publicada': False})

    def put(self, request, entidad_id):
        return Response(datos(guardar(request.user, entidad_id, request.data)))

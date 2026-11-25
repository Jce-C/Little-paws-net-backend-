"""Convocatorias públicas: edición explícita, ámbito y control de concurrencia."""
import hashlib
import json
from urllib.parse import urlsplit
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from seguridad.autorizacion import exigir, invalidar
from seguridad.servicios import auditar, bloqueo_seguridad
from seguridad.serializers import EntradaEstricta
from seguridad.models import BajaAdministrativa
from .models import Fundacion, ProgramaAyuda


class ActividadEntrada(EntradaEstricta, serializers.Serializer):
    titulo = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(max_length=500)
    horario = serializers.CharField(max_length=160)
    requisitos = serializers.CharField(max_length=300)


class CanalEntrada(EntradaEstricta, serializers.Serializer):
    titulo = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(max_length=300)
    url = serializers.URLField(max_length=300)

    def validate_url(self, value):
        url = urlsplit(value)
        if url.scheme != 'https' or not url.hostname or url.username or url.password:
            raise serializers.ValidationError(_('Usa una dirección HTTPS sin credenciales.'))
        return value


class ProgramaEntrada(EntradaEstricta, serializers.Serializer):
    version = serializers.CharField(max_length=64)
    actividades = ActividadEntrada(many=True, allow_empty=True, max_length=8)
    canales = CanalEntrada(many=True, allow_empty=True, max_length=4)
    publicada = serializers.BooleanField()
    confirmar_publicacion = serializers.BooleanField(default=False)

    def validate(self, values):
        if len(values['actividades']) > 8 or len(values['canales']) > 4:
            raise serializers.ValidationError(_('Publica como máximo ocho actividades y cuatro canales.'))
        for field in ('actividades', 'canales'):
            titles = [row['titulo'].casefold() for row in values[field]]
            if len(titles) != len(set(titles)):
                raise serializers.ValidationError(_('Usa un título distinto para cada actividad o canal.'))
        if values['publicada']:
            if not values['confirmar_publicacion']:
                raise serializers.ValidationError(_('Confirma que la organización autoriza publicar estas actividades y canales.'))
            if not values['actividades'] and not values['canales']:
                raise serializers.ValidationError(_('Añade una actividad o un canal antes de publicar.'))
        return values


def datos(profile):
    data = {key: getattr(profile, key) for key in ('actividades', 'canales', 'publicada')} if profile else {
        'actividades': [], 'canales': [], 'publicada': False,
    }
    data['version'] = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return data


def descriptor(foundation):
    profile = getattr(foundation, 'programa_ayuda', None)
    if not profile or not profile.publicada:
        return None
    return {
        'actividades': profile.actividades if foundation.acepta_voluntarios else [],
        'canales': profile.canales,
    }


def autorizada(actor, pk):
    exigir(actor, 'ayudas.gestionar', entidad_id=pk)
    return get_object_or_404(Fundacion.objects.select_related('entidad__estado_verificacion'), pk=pk)


class ConflictoPrograma(APIException):
    status_code = 409
    default_detail = _('La publicación cambió. Actualiza antes de guardar; tus cambios no se han aplicado.')


@transaction.atomic
def guardar(actor, pk, values):
    bloqueo_seguridad()
    invalidar()
    foundation = autorizada(actor, pk)
    # Serialize both editors against the same foundation, including first create.
    Fundacion.objects.select_for_update().get(pk=pk)
    if BajaAdministrativa.objects.filter(tipo='entidades', objeto_id=pk, activo=False).exists():
        raise ValidationError(_('Restaura la organización antes de editar su convocatoria.'))
    entry = ProgramaEntrada(data=values)
    entry.is_valid(raise_exception=True)
    clean = entry.validated_data
    before = datos(ProgramaAyuda.objects.filter(fundacion=foundation).first())
    if clean['version'] != before['version']:
        raise ConflictoPrograma()
    if clean['publicada'] and foundation.entidad.estado_verificacion.nombre != 'Verificada':
        raise ValidationError(_('La organización debe estar verificada antes de publicar.'))
    if clean['publicada'] and clean['actividades'] and not foundation.acepta_voluntarios:
        raise ValidationError(_('Activa la recepción de voluntarios antes de publicar actividades.'))
    profile, _created = ProgramaAyuda.objects.update_or_create(fundacion=foundation, defaults={
        **{key: clean[key] for key in ('actividades', 'canales', 'publicada')}, 'editor': actor,
    })
    auditar(actor, 'ayudas.programa_publico', 'ayudas', pk, pk,
            motivo='Convocatoria autorizada' if profile.publicada else 'Convocatoria guardada sin publicar',
            anterior=before, nuevo=datos(profile))
    return datos(profile)


class ProgramaAdministrarView(APIView):
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        return response

    def get(self, request, fundacion_id):
        foundation = autorizada(request.user, fundacion_id)
        return Response(datos(ProgramaAyuda.objects.filter(fundacion=foundation).first()))

    def patch(self, request, fundacion_id):
        return Response(guardar(request.user, fundacion_id, request.data))

"""Foto pública de perfil con autorización explícita, separada de los datos privados."""
import logging
from pathlib import Path
import re
import uuid

from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from core.public_images import normalizar, StorageUnavailable
from seguridad.autorizacion import invalidar
from seguridad.servicios import auditar, bloqueo_seguridad

from .models import FotoPublicaPerfil
from accounts.models import Usuario



MAX_AVATAR = 64 * 1024




def raiz():
    return (Path(settings.LPN_PRIVATE_ROOT) / 'profile-photos').resolve()


def ruta(clave):
    if not re.fullmatch(r'[a-f0-9]{32}\.webp', clave):
        raise ValidationError(_('Foto de perfil no disponible.'))
    path = (raiz() / clave).resolve()
    if path.parent != raiz():
        raise ValidationError(_('Foto de perfil no disponible.'))
    return path


def borrar(clave):
    try:
        ruta(clave).unlink(missing_ok=True)
    except (OSError, ValidationError):
        logging.getLogger(__name__).warning('No se pudo retirar una copia de foto de perfil obsoleta.')


def propietario(actor, bloquear=False):
    qs = Usuario.objects.select_for_update() if bloquear else Usuario.objects.all()
    user = get_object_or_404(qs, pk=actor.pk, is_active=True)
    return user


def descriptor(user):
    photo = getattr(user, 'foto_comunidad', None)
    if not user.is_active or photo is None or not photo.publicada:
        return None
    return {'url': f'/api/comunidad/perfiles/{photo.public_id}/foto/',
            'ancho': photo.ancho, 'alto': photo.alto, 'bytes': photo.tamano_bytes}


def publicar(actor, archivo, confirmar):
    if confirmar is not True:
        raise ValidationError(_('Confirma que deseas mostrar esta foto públicamente en Comunidad.'))
    propietario(actor)
    data, width, height = normalizar(archivo, max_side=256, max_output=MAX_AVATAR)
    written = None
    try:
        with transaction.atomic():
            bloqueo_seguridad()
            invalidar()
            user = propietario(actor, bloquear=True)
            old = FotoPublicaPerfil.objects.filter(usuario=user).first()
            key = uuid.uuid4().hex + '.webp'
            raiz().mkdir(parents=True, exist_ok=True)
            written = ruta(key)
            with written.open('xb') as stream:
                stream.write(data)
            photo, _created = FotoPublicaPerfil.objects.update_or_create(usuario=user, defaults={
                'clave': key, 'ancho': width, 'alto': height,
                'tamano_bytes': len(data), 'publicada': True, 'public_id': uuid.uuid4()})
            auditar(actor, 'perfil.foto_publicar', 'usuarios', user.pk,
                    motivo='Autorización explícita de foto de perfil pública',
                    nuevo={'ancho': width, 'alto': height, 'bytes': len(data)}, reemplazo=bool(old))
            if old:
                transaction.on_commit(lambda: borrar(old.clave))
            return photo
    except Exception as exc:
        if written:
            borrar(written.name)
        if isinstance(exc, OSError):
            raise StorageUnavailable() from exc
        raise


@transaction.atomic
def retirar(actor):
    bloqueo_seguridad()
    invalidar()
    user = propietario(actor, bloquear=True)
    photo = get_object_or_404(FotoPublicaPerfil.objects.select_for_update(), usuario=user)
    if photo.publicada:
        photo.publicada = False
        photo.save(update_fields=['publicada'])
        auditar(actor, 'perfil.foto_retirar', 'usuarios', user.pk,
                motivo='Retirada de foto de perfil pública')
        transaction.on_commit(lambda: borrar(photo.clave))

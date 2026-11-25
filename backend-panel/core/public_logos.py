"""Logo público autorizado, separado de los documentos de la organización."""
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
from seguridad.autorizacion import exigir, invalidar
from seguridad.servicios import auditar, bloqueo_seguridad
from seguridad.models import BajaAdministrativa
from .models import EntidadVerificable, LogoPublicoEntidad
from django.db.models import Q


MAX_LOGO = 96 * 1024


def disponibles():
    bajas = BajaAdministrativa.objects.filter(tipo='entidades', activo=False).values('objeto_id')
    return EntidadVerificable.objects.filter(estado_verificacion__nombre='Verificada').filter(
        Q(fundacion__isnull=False) | Q(clinica__isnull=False) | Q(tienda__isnull=False)
    ).exclude(pk__in=bajas)


def raiz():
    return (Path(settings.LPN_PRIVATE_ROOT) / 'organization-logos').resolve()


def ruta(clave):
    if not re.fullmatch(r'[a-f0-9]{32}\.webp', clave):
        raise ValidationError(_('Logo no disponible.'))
    path = (raiz() / clave).resolve()
    if path.parent != raiz():
        raise ValidationError(_('Logo no disponible.'))
    return path


def borrar(clave):
    try:
        ruta(clave).unlink(missing_ok=True)
    except (OSError, ValidationError):
        logging.getLogger(__name__).warning('No se pudo retirar una copia de logo obsoleta.')


def autorizado(actor, entidad_id, bloquear=False):
    exigir(actor, 'entidades.editar')
    qs = EntidadVerificable.objects.select_for_update() if bloquear else EntidadVerificable.objects.all()
    return get_object_or_404(qs, pk=entidad_id)


def descriptor(entity):
    logo = getattr(entity, 'logo_publico', None)
    if logo is None or not logo.publicada:
        return None
    return {'url': f'/api/red/organizaciones/{entity.pk}/logo/?v={int(logo.fecha_publicacion.timestamp() * 1_000_000)}',
            'ancho': logo.ancho, 'alto': logo.alto, 'bytes': logo.tamano_bytes}


def publicar(actor, entidad_id, archivo, confirmar):
    if confirmar is not True:
        raise ValidationError(_('Confirma que tienes autorización para publicar el logo de esta organización.'))
    autorizado(actor, entidad_id)
    if not disponibles().filter(pk=entidad_id).exists():
        raise ValidationError(_('La organización debe estar activa, verificada y registrada como fundación, clínica o tienda.'))
    data, width, height = normalizar(archivo, max_side=512, max_output=MAX_LOGO)
    written = None
    try:
        with transaction.atomic():
            bloqueo_seguridad()
            invalidar()
            entity = autorizado(actor, entidad_id, bloquear=True)
            if not disponibles().filter(pk=entity.pk).exists():
                raise ValidationError(_('La organización debe estar activa, verificada y registrada como fundación, clínica o tienda.'))
            old = LogoPublicoEntidad.objects.filter(entidad=entity).first()
            key = uuid.uuid4().hex + '.webp'
            raiz().mkdir(parents=True, exist_ok=True)
            written = ruta(key)
            with written.open('xb') as stream:
                stream.write(data)
            photo, _created = LogoPublicoEntidad.objects.update_or_create(entidad=entity, defaults={
                'clave': key, 'ancho': width, 'alto': height,
                'tamano_bytes': len(data), 'publicada': True, 'publicador': actor})
            auditar(actor, 'entidad.logo_publicar', 'entidades', entity.pk, entity.pk,
                    motivo='Autorización explícita del logo público de la organización',
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
def retirar(actor, entidad_id):
    bloqueo_seguridad()
    invalidar()
    entity = autorizado(actor, entidad_id, bloquear=True)
    photo = get_object_or_404(LogoPublicoEntidad.objects.select_for_update(), entidad=entity)
    if photo.publicada:
        photo.publicada = False
        photo.save(update_fields=['publicada'])
        auditar(actor, 'entidad.logo_retirar', 'entidades', entity.pk, entity.pk,
                motivo='Retirada del logo público de la organización')
        transaction.on_commit(lambda: borrar(photo.clave))

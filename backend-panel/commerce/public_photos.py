"""Fotografía comercial autorizada, aislada de los documentos privados."""
import logging
from pathlib import Path
import re
import uuid

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from core.public_images import normalizar, MAX_OUTPUT, StorageUnavailable
from seguridad.autorizacion import exigir, invalidar
from seguridad.servicios import auditar, bloqueo_seguridad
from seguridad.models import BajaAdministrativa
from .models import Producto, FotoPublicaProducto


def disponibles():
    bajas = BajaAdministrativa.objects.filter(tipo='entidades', activo=False).values('objeto_id')
    productos = BajaAdministrativa.objects.filter(tipo='productos', activo=False).values('objeto_id')
    return Producto.objects.filter(
        estado_producto__tipo__nombre='estado_producto', estado_producto__nombre='Disponible',
        tienda__entidad__estado_verificacion__nombre='Verificada',
    ).exclude(tienda_id__in=bajas).exclude(pk__in=productos)


def raiz():
    return (Path(settings.LPN_PRIVATE_ROOT) / 'product-photos').resolve()


def ruta(clave):
    if not re.fullmatch(r'[a-f0-9]{32}\.webp', clave):
        raise ValidationError('Fotografía no disponible.')
    path = (raiz() / clave).resolve()
    if path.parent != raiz():
        raise ValidationError('Fotografía no disponible.')
    return path


def borrar(clave):
    try:
        ruta(clave).unlink(missing_ok=True)
    except (OSError, ValidationError):
        logging.getLogger(__name__).warning('No se pudo retirar una fotografía comercial obsoleta.')


def autorizado(actor, producto_id, bloquear=False):
    qs = Producto.objects.select_for_update() if bloquear else Producto.objects.all()
    product = get_object_or_404(qs, pk=producto_id)
    exigir(actor, 'producto.gestionar', entidad_id=product.tienda_id)
    return product


def descriptor(product):
    photo = getattr(product, 'foto_publica', None)
    if photo is None or not photo.publicada or photo.tienda_id != product.tienda_id:
        return None
    return {'url': f'/api/catalogo/productos/{product.pk}/foto/?v={int(photo.fecha_publicacion.timestamp() * 1_000_000)}',
            'ancho': photo.ancho, 'alto': photo.alto, 'bytes': photo.tamano_bytes}


def publicar(actor, producto_id, archivo, confirmar):
    if confirmar is not True:
        raise ValidationError('Confirma que tienes autorización para publicar esta fotografía.')
    autorizado(actor, producto_id)
    if not disponibles().filter(pk=producto_id).exists():
        raise ValidationError('El producto debe estar disponible en una tienda verificada.')
    data, width, height = normalizar(archivo)
    written = None
    try:
        with transaction.atomic():
            bloqueo_seguridad()
            invalidar()
            product = autorizado(actor, producto_id, bloquear=True)
            if not disponibles().filter(pk=product.pk).exists():
                raise ValidationError('El producto debe estar disponible en una tienda verificada.')
            old = FotoPublicaProducto.objects.filter(producto=product).first()
            key = uuid.uuid4().hex + '.webp'
            raiz().mkdir(parents=True, exist_ok=True)
            written = ruta(key)
            with written.open('xb') as stream:
                stream.write(data)
            photo, _ = FotoPublicaProducto.objects.update_or_create(producto=product, defaults={
                'tienda_id': product.tienda_id, 'clave': key, 'ancho': width, 'alto': height,
                'tamano_bytes': len(data), 'publicada': True, 'publicador': actor})
            auditar(actor, 'producto.foto_publicar', 'producto', product.pk, product.tienda_id,
                    motivo='Autorización explícita de fotografía comercial pública',
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
def retirar(actor, producto_id):
    bloqueo_seguridad()
    invalidar()
    product = autorizado(actor, producto_id, bloquear=True)
    photo = get_object_or_404(FotoPublicaProducto.objects.select_for_update(), producto=product)
    if photo.publicada:
        photo.publicada = False
        photo.save(update_fields=['publicada'])
        auditar(actor, 'producto.foto_retirar', 'producto', product.pk, product.tienda_id,
                motivo='Retirada de autorización de fotografía comercial')
        transaction.on_commit(lambda: borrar(photo.clave))

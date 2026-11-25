"""Fotografías públicas explícitas, normalizadas y separadas del expediente."""
from pathlib import Path
import logging
import re
import uuid

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from seguridad.autorizacion import exigir, invalidar
from seguridad.servicios import auditar, bloqueo_seguridad
from adoption.consultas import disponibles_adopcion
from .models import CustodiaMascota, FotoPublicaMascota, FotoGaleriaMascota, Mascota

from core.public_images import normalizar, MAX_INPUT, MAX_OUTPUT, StorageUnavailable


def raiz():
    return (Path(settings.LPN_PRIVATE_ROOT) / "pet-photos").resolve()


def ruta(clave):
    if not re.fullmatch(r"[a-f0-9]{32}\.webp", clave):
        raise ValidationError("Fotografía no disponible.")
    target = (raiz() / clave).resolve()
    if target.parent != raiz():
        raise ValidationError("Fotografía no disponible.")
    return target




def custodia_autorizada(actor, mascota_id, bloquear=True):
    pets = Mascota.objects.select_for_update() if bloquear else Mascota.objects.all()
    custodias = CustodiaMascota.objects.select_for_update() if bloquear else CustodiaMascota.objects.all()
    pet = get_object_or_404(pets, pk=mascota_id)
    custody = get_object_or_404(custodias, mascota=pet, fecha_fin__isnull=True)
    exigir(actor, "mascotas.publicar_adopcion", entidad_id=custody.fundacion_id)
    return pet, custody


def borrar_obsoleto(clave):
    try:
        ruta(clave).unlink(missing_ok=True)
    except (OSError, ValidationError):
        logging.getLogger(__name__).warning("No se pudo retirar un archivo de fotografía obsoleto.")


def publicar(actor, mascota_id, archivo, confirmar, adicional=False):
    if confirmar is not True:
        raise ValidationError("Confirma que tienes autorización para publicar esta fotografía.")
    pet, _ = custodia_autorizada(actor, mascota_id, bloquear=False)
    if not disponibles_adopcion().filter(pk=pet.pk).exists():
        raise ValidationError("La fotografía requiere una ficha disponible para adopción.")
    data, width, height = normalizar(archivo)
    written = None
    try:
        with transaction.atomic():
            bloqueo_seguridad()
            invalidar()
            pet, custody = custodia_autorizada(actor, mascota_id)
            if not disponibles_adopcion().filter(pk=pet.pk).exists():
                raise ValidationError("La fotografía requiere una ficha disponible para adopción.")
            if adicional and FotoGaleriaMascota.objects.filter(mascota=pet, publicada=True).count() >= 5:
                raise ValidationError("La galería admite cinco fotografías adicionales a la portada.")
            previous = None if adicional else FotoPublicaMascota.objects.filter(mascota=pet).first()
            old_key = previous.clave if previous else None
            key = uuid.uuid4().hex + ".webp"
            raiz().mkdir(parents=True, exist_ok=True)
            written = ruta(key)
            with written.open("xb") as destination:
                destination.write(data)
            metadata = {
                "fundacion": custody.fundacion, "clave": key, "tamano_bytes": len(data),
                "ancho": width, "alto": height, "publicada": True, "publicador": actor,
            }
            if adicional:
                photo = FotoGaleriaMascota.objects.create(mascota=pet, **metadata)
            else:
                photo, _ = FotoPublicaMascota.objects.update_or_create(mascota=pet, defaults=metadata)
            auditar(actor, "mascotas.foto_publicar", "mascotas", pet.pk, custody.fundacion_id,
                    motivo="Confirmación explícita de autorización para publicar la fotografía",
                    nuevo={"ancho": width, "alto": height, "bytes": len(data)}, reemplazo=bool(old_key))
            if old_key:
                transaction.on_commit(lambda: borrar_obsoleto(old_key))
            return photo
    except Exception as failure:
        if written is not None:
            borrar_obsoleto(written.name)
        if isinstance(failure, OSError):
            raise StorageUnavailable() from failure
        raise


@transaction.atomic
def retirar(actor, mascota_id, foto_id=None):
    bloqueo_seguridad()
    invalidar()
    pet, custody = custodia_autorizada(actor, mascota_id)
    source = FotoGaleriaMascota.objects.select_for_update().filter(pk=foto_id) if foto_id is not None else FotoPublicaMascota.objects.select_for_update()
    photo = get_object_or_404(source, mascota=pet)
    if photo.publicada:
        photo.publicada = False
        photo.save(update_fields=["publicada"])
        auditar(actor, "mascotas.foto_retirar", "mascotas", pet.pk, custody.fundacion_id, motivo="Retirada de la autorización de fotografía pública")
        transaction.on_commit(lambda: borrar_obsoleto(photo.clave))


def foto_descriptor(mascota, fundacion_id):
    """Solo metadatos públicos; el archivo se comprueba en su GET autorizado."""
    photo = getattr(mascota, "foto_publica", None)
    if photo is None or not photo.publicada or photo.fundacion_id != fundacion_id:
        return None
    version = int(photo.fecha_publicacion.timestamp() * 1_000_000)
    return {
        "url": f"/api/adopcion/mascotas/{mascota.pk}/foto/?v={version}",
        "ancho": photo.ancho, "alto": photo.alto, "bytes": photo.tamano_bytes,
    }


def galeria_descriptor(mascota, fundacion_id):
    cover = foto_descriptor(mascota, fundacion_id)
    rows = [cover] if cover else []
    for photo in FotoGaleriaMascota.objects.filter(mascota=mascota, fundacion_id=fundacion_id, publicada=True).order_by("pk")[:5]:
        rows.append({"url": f"/api/adopcion/mascotas/{mascota.pk}/fotos/{photo.pk}/?v={int(photo.fecha_publicacion.timestamp() * 1_000_000)}",
                     "ancho": photo.ancho, "alto": photo.alto, "bytes": photo.tamano_bytes})
    return rows

"""Bounded portrait inside an already-authorized, non-cacheable medical response."""
import base64
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError
from core.public_images import normalizar
from .models import CustodiaMascota, FotoPublicaMascota
from . import public_photos


def miniatura(pet):
    personal = getattr(pet, 'perfil_personal', None)
    if personal is not None and personal.foto:
        return {'tipo':'image/webp','ancho':personal.ancho,'alto':personal.alto,'datos':base64.b64encode(bytes(personal.foto)).decode('ascii')}
    # Reuse the authorized portrait from the current/latest custodian only.
    # A closed adoption custody may retain its portrait in the private record.
    custody = CustodiaMascota.objects.filter(mascota=pet, fecha_fin__isnull=True).first()
    if custody is None:
        custody = CustodiaMascota.objects.filter(mascota=pet).order_by('-fecha_inicio', '-pk').first()
    if custody is None:
        return None
    photo = FotoPublicaMascota.objects.filter(mascota=pet, fundacion=custody.fundacion, publicada=True).first()
    if photo is None:
        return None
    try:
        with public_photos.ruta(photo.clave).open('rb') as stream:
            content = stream.read(public_photos.MAX_OUTPUT + 1)
        if len(content) != photo.tamano_bytes or len(content) > public_photos.MAX_OUTPUT:
            return None
        data, width, height = normalizar(SimpleUploadedFile('retrato.webp', content, 'image/webp'), max_side=160, max_output=32 * 1024)
    except (OSError, ValidationError):
        return None
    return {'tipo': 'image/webp', 'ancho': width, 'alto': height, 'datos': base64.b64encode(data).decode('ascii')}

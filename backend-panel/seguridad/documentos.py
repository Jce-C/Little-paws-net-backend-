"""Almacenamiento local privado: sin URLs públicas ni nombres enviados por el usuario."""
import hashlib
import uuid
from pathlib import Path

from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from . import flujos as f
from .models import DocumentoPrivado, ReclamacionMascota
from .servicios import auditar


def raiz():
    return Path(settings.LPN_PRIVATE_ROOT).resolve()


def ruta(doc):
    path = (raiz() / doc.clave).resolve()
    if path.parent != raiz():
        raise ValidationError("Archivo no disponible")
    return path


def cargar(actor, recurso, pk, archivo):
    doc = None
    try:
        with transaction.atomic():
            objeto = f.objeto_privado(recurso, pk)
            f.obtener(type(objeto), pk, True)
            doc = _cargar(actor, recurso, pk, archivo)
        return doc
    except Exception:
        if doc is not None:
            ruta(doc).unlink(missing_ok=True)
        raise


def _cargar(actor, recurso, pk, archivo):
    f.activo(actor)
    obj = f.objeto_privado(recurso, pk)
    permitido = False
    if recurso == "expediente":
        permitido = f.dueno(actor, obj)
    elif recurso == "verificacion":
        permitido = obj.usuario_solicitante_id == actor.pk and obj.estado_solicitud.nombre in ("Pendiente", "Correcciones")
    elif recurso == "reclamacion":
        permitido = obj.reclamante_id == actor.pk and obj.estado == "PENDIENTE"
    elif recurso == "aporte":
        permitido = obj.usuario_padrino_id == actor.pk and obj.estado_apadrinamiento.nombre in ("En espera", "Aceptado")
    elif recurso == "adopcion":
        permitido = obj.usuario_adoptante_id == actor.pk and obj.estado_adopcion.nombre == "Pendiente"
    if not permitido:
        raise PermissionDenied("No puedes adjuntar documentos a este registro")
    if not archivo or archivo.size > 10 * 1024 * 1024 or archivo.size == 0:
        raise ValidationError("El archivo debe ocupar entre 1 byte y 10 MB")
    contenido = archivo.read(10 * 1024 * 1024 + 1)
    if len(contenido) > 10 * 1024 * 1024:
        raise ValidationError("Archivo demasiado grande")
    formatos = ((b"%PDF-", "application/pdf", ".pdf"),
                (b"\x89PNG\r\n\x1a\n", "image/png", ".png"), (b"\xff\xd8\xff", "image/jpeg", ".jpg"))
    formato = next((x for x in formatos if contenido.startswith(x[0])), None)
    if formato is None:
        raise ValidationError("Solo se admiten documentos PDF e imágenes PNG/JPEG")
    raiz().mkdir(parents=True, exist_ok=True)
    clave = uuid.uuid4().hex + formato[2]
    path = raiz() / clave
    try:
        with transaction.atomic():
            doc = DocumentoPrivado.objects.create(propietario=actor, recurso=recurso, objeto_id=pk,
                clave=clave, mime=formato[1], tamano=len(contenido), sha256=hashlib.sha256(contenido).hexdigest())
            with path.open("xb") as destino:
                destino.write(contenido)
            auditar(actor, "documento.cargar", "soporte", doc.pk)
        return doc
    except Exception:
        path.unlink(missing_ok=True)
        raise

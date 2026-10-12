"""Reglas de negocio del fondo externo, sin procesamiento de pagos."""

from django.db import IntegrityError, transaction

from core.crypto import cifrar

from .models import FondoExterno
from .permissions import administrador_puede


class FondoError(ValueError):
    pass


class FondoPermisoError(FondoError):
    pass


@transaction.atomic
def crear_fondo_externo(*, usuario_actor, nombre, instrucciones_transferencia):
    if not administrador_puede(usuario_actor, "fondo.gestionar"):
        raise FondoPermisoError("No tiene permiso para configurar fondos")
    nombre = nombre.strip()
    instrucciones_transferencia = instrucciones_transferencia.strip()
    if not nombre or not instrucciones_transferencia:
        raise FondoError("Nombre e instrucciones son obligatorios")
    if FondoExterno.objects.filter(nombre__iexact=nombre).exists():
        raise FondoError("Ya existe un fondo con ese nombre")
    try:
        return FondoExterno.objects.create(
            nombre=nombre,
            datos_transferencia_cifrados=cifrar(instrucciones_transferencia),
        )
    except IntegrityError as exc:
        raise FondoError("Ya existe un fondo con ese nombre") from exc

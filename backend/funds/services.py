"""Reglas de negocio del fondo externo, sin procesamiento de pagos."""

from django.db import IntegrityError, transaction

from core.crypto import cifrar
from core.models import ValorMaestro

from .models import DonacionGeneral, FondoExterno, HistorialEstadoDonacion
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


@transaction.atomic
def crear_compromiso_donacion(*, usuario_donante, fondo_externo, monto_comprometido):
    if not usuario_donante.is_active:
        raise FondoPermisoError("La cuenta del donante no está activa")
    if monto_comprometido <= 0:
        raise FondoError("El monto comprometido debe ser positivo")
    estado = ValorMaestro.objects.get(tipo__nombre="estado_donacion", nombre="Comprometida")
    donacion = DonacionGeneral.objects.create(
        fondo_externo=fondo_externo,
        usuario_donante=usuario_donante,
        estado_donacion=estado,
        monto_comprometido=monto_comprometido,
    )
    HistorialEstadoDonacion.objects.create(
        donacion=donacion,
        estado_nuevo=estado,
        usuario_actor=usuario_donante,
        observacion="Registro del compromiso; no confirma recepción de dinero",
    )
    return donacion

"""Operaciones de apadrinamiento externo y confirmación exclusiva de fundación."""

from decimal import Decimal

from django.db import transaction
from seguridad.autorizacion import puede

from core.crypto import descifrar
from core.models import EntidadMiembroRol, Rol, ValorMaestro
from .models import (
    Apadrinamiento, CasoRescate, ConfirmacionAporte, CuentaFundacion,
    CuentaRevelada, HistorialEstadoApadrinamiento,
)


class ApadrinamientoError(ValueError):
    pass


def miembro_puede(fundacion_id, usuario_id, codigo_permiso, objeto_id=None):
    return puede(usuario_id, codigo_permiso, entidad_id=fundacion_id, objeto_id=objeto_id)


@transaction.atomic
def crear_compromiso(*, reporte_id, usuario_padrino_id, monto):
    if monto <= Decimal("0"):
        raise ApadrinamientoError("El monto debe ser positivo")
    caso = CasoRescate.objects.filter(reporte_id=reporte_id).first()
    if caso is None:
        raise ApadrinamientoError("El reporte aún no fue aceptado por una fundación")
    estado = ValorMaestro.objects.get(tipo__nombre="estado_apadrinamiento", nombre="En espera")
    apad = Apadrinamiento.objects.create(
        reporte_id=reporte_id, usuario_padrino_id=usuario_padrino_id,
        estado_apadrinamiento=estado, monto_comprometido=monto,
    )
    HistorialEstadoApadrinamiento.objects.create(
        apadrinamiento=apad, estado_anterior=None, estado_nuevo=estado,
        usuario_actor_id=usuario_padrino_id,
        observacion="Compromiso creado; no representa dinero recibido",
    )
    return apad


@transaction.atomic
def revelar_cuenta(*, apadrinamiento_id, usuario_padrino_id):
    try:
        apad = Apadrinamiento.objects.select_related("reporte__casorescate").get(pk=apadrinamiento_id)
    except Apadrinamiento.DoesNotExist as exc:
        raise ApadrinamientoError("Apadrinamiento inexistente") from exc
    if apad.usuario_padrino_id != usuario_padrino_id:
        raise ApadrinamientoError("Solo el padrino puede consultar la cuenta")
    try:
        fundacion_id = apad.reporte.casorescate.fundacion_id
    except CasoRescate.DoesNotExist as exc:
        raise ApadrinamientoError("El reporte no tiene fundación receptora") from exc
    cuenta = CuentaFundacion.objects.filter(fundacion_id=fundacion_id, activa=True).order_by("-fecha_registro").first()
    if cuenta is None:
        raise ApadrinamientoError("La fundación aún no publicó una cuenta de transferencia")
    numero = descifrar(cuenta.numero_cuenta_cifrado)
    CuentaRevelada.objects.get_or_create(apadrinamiento=apad, cuenta=cuenta)
    return cuenta, numero


@transaction.atomic
def confirmar_aporte(*, apadrinamiento_id, usuario_confirmador_id, monto):
    if monto <= Decimal("0"):
        raise ApadrinamientoError("El monto debe ser positivo")
    try:
        apad = Apadrinamiento.objects.select_for_update().select_related(
            "reporte__casorescate", "estado_apadrinamiento"
        ).get(pk=apadrinamiento_id)
    except Apadrinamiento.DoesNotExist as exc:
        raise ApadrinamientoError("Apadrinamiento inexistente") from exc
    fundacion_id = apad.reporte.casorescate.fundacion_id
    if not miembro_puede(fundacion_id, usuario_confirmador_id, "aporte.confirmar", apad.pk):
        raise ApadrinamientoError("Solo la fundación receptora puede confirmar el aporte")
    if apad.estado_apadrinamiento.nombre not in ("En espera", "Aceptado"):
        raise ApadrinamientoError("El compromiso no admite confirmaciones")
    confirmado = sum(
        apad.confirmacionaporte_set.values_list("monto_confirmado", flat=True),
        Decimal("0"),
    )
    if confirmado + monto > apad.monto_comprometido:
        raise ApadrinamientoError("La suma confirmada supera el compromiso")
    confirmacion = ConfirmacionAporte.objects.create(
        apadrinamiento=apad,
        monto_confirmado=monto,
        usuario_confirmador_id=usuario_confirmador_id,
    )
    if apad.estado_apadrinamiento.nombre == "En espera":
        anterior = apad.estado_apadrinamiento
        nuevo = ValorMaestro.objects.get(tipo__nombre="estado_apadrinamiento", nombre="Aceptado")
        apad.estado_apadrinamiento = nuevo
        apad.save(update_fields=["estado_apadrinamiento"])
        HistorialEstadoApadrinamiento.objects.create(
            apadrinamiento=apad, estado_anterior=anterior, estado_nuevo=nuevo,
            usuario_actor_id=usuario_confirmador_id,
            observacion="La fundación confirmó recepción de un aporte",
        )
    return confirmacion

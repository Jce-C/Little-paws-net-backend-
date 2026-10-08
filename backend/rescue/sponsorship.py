"""Operaciones de compromisos y confirmaciones de dinero externo."""

from decimal import Decimal

from django.db import transaction

from core.crypto import descifrar
from core.models import ValorMaestro

from .models import (
    Apadrinamiento, CasoRescate, ConfirmacionAporte, CuentaFundacion,
    CuentaRevelada, HistorialEstadoApadrinamiento,
)
from .services import miembro_puede


class ApadrinamientoError(ValueError):
    pass


@transaction.atomic
def crear_compromiso(*, reporte_id, usuario_padrino_id, monto):
    if monto <= Decimal("0"):
        raise ApadrinamientoError("El monto debe ser positivo")
    caso = CasoRescate.objects.select_related("estado_caso").filter(reporte_id=reporte_id).first()
    if caso is None or caso.estado_caso.nombre != "En atención":
        raise ApadrinamientoError("El reporte no tiene un caso activo")
    estado = ValorMaestro.objects.get(tipo__nombre="estado_apadrinamiento", nombre="En espera")
    apadrinamiento = Apadrinamiento.objects.create(
        reporte_id=reporte_id, usuario_padrino_id=usuario_padrino_id,
        estado_apadrinamiento=estado, monto_comprometido=monto,
    )
    HistorialEstadoApadrinamiento.objects.create(
        apadrinamiento=apadrinamiento, estado_nuevo=estado,
        usuario_actor_id=usuario_padrino_id,
        observacion="Compromiso creado; no equivale a dinero recibido",
    )
    return apadrinamiento


@transaction.atomic
def revelar_cuenta(*, apadrinamiento_id, usuario_padrino_id):
    try:
        apadrinamiento = Apadrinamiento.objects.select_related("reporte__casorescate").get(
            pk=apadrinamiento_id
        )
    except Apadrinamiento.DoesNotExist as exc:
        raise ApadrinamientoError("Apadrinamiento inexistente") from exc
    if apadrinamiento.usuario_padrino_id != usuario_padrino_id:
        raise ApadrinamientoError("Solo el padrino puede consultar la cuenta")
    try:
        fundacion_id = apadrinamiento.reporte.casorescate.fundacion_id
    except CasoRescate.DoesNotExist as exc:
        raise ApadrinamientoError("El reporte no tiene fundación receptora") from exc
    cuenta = CuentaFundacion.objects.filter(
        fundacion_id=fundacion_id, activa=True
    ).order_by("-fecha_registro", "-pk").first()
    if cuenta is None:
        raise ApadrinamientoError("La fundación no tiene una cuenta activa")
    numero = descifrar(cuenta.numero_cuenta_cifrado)
    CuentaRevelada.objects.get_or_create(apadrinamiento=apadrinamiento, cuenta=cuenta)
    return cuenta, numero


@transaction.atomic
def confirmar_aporte(*, apadrinamiento_id, usuario_confirmador_id, monto):
    if monto <= Decimal("0"):
        raise ApadrinamientoError("El monto debe ser positivo")
    try:
        apadrinamiento = Apadrinamiento.objects.select_for_update().select_related(
            "reporte__casorescate", "estado_apadrinamiento"
        ).get(pk=apadrinamiento_id)
    except Apadrinamiento.DoesNotExist as exc:
        raise ApadrinamientoError("Apadrinamiento inexistente") from exc
    fundacion_id = apadrinamiento.reporte.casorescate.fundacion_id
    if not miembro_puede(fundacion_id, usuario_confirmador_id, "aporte.confirmar"):
        raise ApadrinamientoError("Solo la fundación receptora puede confirmar")
    if apadrinamiento.estado_apadrinamiento.nombre not in ("En espera", "Aceptado"):
        raise ApadrinamientoError("El compromiso no admite confirmaciones")
    confirmado = sum(
        apadrinamiento.confirmacionaporte_set.values_list("monto_confirmado", flat=True),
        Decimal("0"),
    )
    if confirmado + monto > apadrinamiento.monto_comprometido:
        raise ApadrinamientoError("La suma confirmada supera el compromiso")
    confirmacion = ConfirmacionAporte.objects.create(
        apadrinamiento=apadrinamiento, monto_confirmado=monto,
        usuario_confirmador_id=usuario_confirmador_id,
    )
    if apadrinamiento.estado_apadrinamiento.nombre == "En espera":
        anterior = apadrinamiento.estado_apadrinamiento
        nuevo = ValorMaestro.objects.get(tipo__nombre="estado_apadrinamiento", nombre="Aceptado")
        apadrinamiento.estado_apadrinamiento = nuevo
        apadrinamiento.save(update_fields=["estado_apadrinamiento"])
        HistorialEstadoApadrinamiento.objects.create(
            apadrinamiento=apadrinamiento, estado_anterior=anterior,
            estado_nuevo=nuevo, usuario_actor_id=usuario_confirmador_id,
            observacion="Recepción confirmada por la fundación",
        )
    return confirmacion

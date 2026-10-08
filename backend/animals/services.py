"""Custodia, autorización temporal y acceso seguro al expediente."""

import hashlib
import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from core.models import ValorMaestro, Veterinario
from rescue.models import CasoRescate, Reporte
from rescue.services import miembro_puede

from .models import (
    AutorizacionExpediente, CodigoQRExpediente, CustodiaMascota,
    HistorialMedico, Mascota,
)


class ExpedienteError(ValueError):
    pass


@transaction.atomic
def registrar_mascota_caso(*, caso_id, usuario_id, datos):
    try:
        caso = CasoRescate.objects.select_for_update().select_related("estado_caso").get(pk=caso_id)
    except CasoRescate.DoesNotExist as exc:
        raise ExpedienteError("Caso inexistente") from exc
    if caso.estado_caso.nombre != "En atención":
        raise ExpedienteError("El caso no está activo")
    if not miembro_puede(caso.fundacion_id, usuario_id, "expediente.autorizar"):
        raise ExpedienteError("Sin autorización para esta fundación")
    reporte = Reporte.objects.select_for_update().get(pk=caso.reporte_id)
    if reporte.mascota_id is not None:
        raise ExpedienteError("El caso ya tiene una mascota identificada")
    mascota = Mascota.objects.create(
        raza=datos["raza"], nombre=datos.get("nombre", ""),
        estado_mascota=ValorMaestro.objects.get(tipo__nombre="estado_mascota", nombre="En rescate"),
        fecha_nacimiento=datos.get("fecha_nacimiento"),
        es_estimada=datos.get("es_estimada", False),
        sexo=datos.get("sexo"), tamano=datos.get("tamano"),
    )
    reporte.mascota = mascota
    reporte.save(update_fields=["mascota", "fecha_actualizacion"])
    return mascota


def _custodia_autorizada(mascota_id, usuario_id):
    custodias = list(CustodiaMascota.objects.select_related("fundacion__entidad").filter(
        mascota_id=mascota_id, fecha_fin__isnull=True,
    )[:2])
    if len(custodias) != 1:
        raise ExpedienteError("La mascota debe tener una sola custodia activa")
    custodia = custodias[0]
    if not miembro_puede(custodia.fundacion_id, usuario_id, "expediente.autorizar"):
        raise ExpedienteError("Sin autorización de la fundación custodiante")
    return custodia


@transaction.atomic
def registrar_custodia(*, caso_id, usuario_id):
    try:
        caso = CasoRescate.objects.select_for_update().select_related("reporte", "estado_caso").get(pk=caso_id)
    except CasoRescate.DoesNotExist as exc:
        raise ExpedienteError("Caso inexistente") from exc
    if caso.estado_caso.nombre != "En atención" or caso.reporte.mascota_id is None:
        raise ExpedienteError("El caso debe estar activo y tener mascota identificada")
    if not miembro_puede(caso.fundacion_id, usuario_id, "expediente.autorizar"):
        raise ExpedienteError("Sin autorización para esta fundación")
    if CustodiaMascota.objects.filter(mascota_id=caso.reporte.mascota_id, fecha_fin__isnull=True).exists():
        raise ExpedienteError("La mascota ya tiene custodia activa")
    return CustodiaMascota.objects.create(
        mascota_id=caso.reporte.mascota_id, fundacion=caso.fundacion,
        caso=caso, fecha_inicio=timezone.now(), usuario_registrador_id=usuario_id,
    )


@transaction.atomic
def autorizar_veterinario(*, mascota_id, veterinario_id, usuario_id, dias=7):
    custodia = _custodia_autorizada(mascota_id, usuario_id)
    try:
        veterinario = Veterinario.objects.select_related("entidad__estado_verificacion__tipo", "usuario_profesional").get(
            pk=veterinario_id
        )
    except Veterinario.DoesNotExist as exc:
        raise ExpedienteError("Veterinario inexistente") from exc
    estado = veterinario.entidad.estado_verificacion
    if estado.tipo.nombre != "estado_verificacion" or estado.nombre != "Verificada":
        raise ExpedienteError("El veterinario no está verificado")
    if not veterinario.usuario_profesional.is_active:
        raise ExpedienteError("La cuenta profesional está inactiva")
    return AutorizacionExpediente.objects.create(
        mascota_id=mascota_id, custodia=custodia, veterinario=veterinario,
        usuario_otorgante_id=usuario_id,
        fecha_expiracion=timezone.now() + timedelta(days=dias),
    )


@transaction.atomic
def regenerar_qr(*, mascota_id, usuario_id, horas=24):
    _custodia_autorizada(mascota_id, usuario_id)
    ahora = timezone.now()
    CodigoQRExpediente.objects.filter(
        mascota_id=mascota_id, fecha_revocacion__isnull=True,
        fecha_expiracion__gt=ahora,
    ).update(fecha_revocacion=ahora)
    token = secrets.token_urlsafe(32)
    qr = CodigoQRExpediente.objects.create(
        mascota_id=mascota_id,
        codigo_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
        fecha_expiracion=ahora + timedelta(hours=horas),
        usuario_creador_id=usuario_id,
    )
    return qr, token


def veterinario_con_acceso(*, mascota_id, usuario_id, token):
    try:
        mascota = Mascota.objects.get(pk=mascota_id)
        veterinario = Veterinario.objects.select_related("entidad__estado_verificacion__tipo").get(
            usuario_profesional_id=usuario_id
        )
    except (Mascota.DoesNotExist, Veterinario.DoesNotExist) as exc:
        raise ExpedienteError("Mascota o veterinario inexistente") from exc
    estado = veterinario.entidad.estado_verificacion
    if estado.tipo.nombre != "estado_verificacion" or estado.nombre != "Verificada":
        raise ExpedienteError("El veterinario no está verificado")
    custodias = list(CustodiaMascota.objects.filter(mascota=mascota, fecha_fin__isnull=True)[:2])
    if len(custodias) != 1:
        raise ExpedienteError("La mascota no tiene custodia única activa")
    custodia = custodias[0]
    ahora = timezone.now()
    if not AutorizacionExpediente.objects.filter(
        mascota=mascota, custodia=custodia, veterinario=veterinario,
        fecha_revocacion__isnull=True, fecha_expiracion__gt=ahora,
    ).exists():
        raise ExpedienteError("No hay autorización vigente para esta mascota")
    if not CodigoQRExpediente.objects.filter(
        mascota=mascota,
        codigo_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
        fecha_revocacion__isnull=True, fecha_expiracion__gt=ahora,
        fecha_creacion__gte=custodia.fecha_inicio,
    ).exists():
        raise ExpedienteError("Código QR inválido o vencido")
    return veterinario


@transaction.atomic
def registrar_atencion(*, mascota_id, usuario_id, token, detalle, fecha_atencion):
    veterinario = veterinario_con_acceso(
        mascota_id=mascota_id, usuario_id=usuario_id, token=token,
    )
    return HistorialMedico.objects.create(
        mascota_id=mascota_id, veterinario=veterinario,
        usuario_registrador_id=usuario_id,
        detalle=detalle, fecha_atencion=fecha_atencion,
    )


@transaction.atomic
def registrar_atencion_externa(*, mascota_id, usuario_id, nombre, matricula, detalle, fecha_atencion):
    _custodia_autorizada(mascota_id, usuario_id)
    if not nombre.strip() or not matricula.strip():
        raise ExpedienteError("Nombre y matrícula profesional son obligatorios")
    return HistorialMedico.objects.create(
        mascota_id=mascota_id, usuario_registrador_id=usuario_id,
        usuario_verificador_id=usuario_id,
        nombre_veterinario_externo=nombre.strip(),
        registro_profesional_externo=matricula.strip(),
        detalle=detalle, fecha_atencion=fecha_atencion,
    )

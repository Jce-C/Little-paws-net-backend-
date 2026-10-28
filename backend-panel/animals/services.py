"""QR revocable y permisos reales de escritura del expediente médico."""

import hashlib
import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from seguridad.autorizacion import puede, usuario_activo

from core.models import EntidadMiembroRol, Rol, Veterinario
from .models import AutorizacionExpediente, CodigoQRExpediente, CustodiaMascota, HistorialMedico, Mascota


class ExpedienteError(ValueError):
    pass


def _custodio_puede(mascota, usuario_id):
    custodias = list(CustodiaMascota.objects.filter(mascota=mascota, fecha_fin__isnull=True)[:2])
    if len(custodias) > 1 or (custodias and mascota.dueno_id is not None):
        raise ExpedienteError("La custodia presenta un conflicto")
    if custodias:
        fundacion_id = custodias[0].fundacion_id
        return puede(usuario_id, "expediente.autorizar", entidad_id=fundacion_id)
    return mascota.dueno_id == usuario_id and usuario_activo(usuario_id)


def _veterinario_verificado(vet):
    estado = vet.entidad.estado_verificacion
    return (
        estado.tipo.nombre == "estado_verificacion"
        and estado.nombre == "Verificada"
        and vet.usuario_profesional.is_active
    )


@transaction.atomic
def autorizar_veterinario(*, mascota_id, veterinario_id, usuario_otorgante_id, horas=24):
    if not 1 <= horas <= 720:
        raise ExpedienteError("La autorización debe durar entre 1 y 720 horas")
    try:
        mascota = Mascota.objects.select_for_update().get(pk=mascota_id)
    except Mascota.DoesNotExist as exc:
        raise ExpedienteError("Mascota inexistente") from exc
    if not _custodio_puede(mascota, usuario_otorgante_id):
        raise ExpedienteError("El usuario no tiene derecho a autorizar esta mascota")
    try:
        vet = Veterinario.objects.select_related(
            "entidad__estado_verificacion__tipo", "usuario_profesional"
        ).get(pk=veterinario_id)
    except Veterinario.DoesNotExist as exc:
        raise ExpedienteError("Veterinario inexistente") from exc
    if not _veterinario_verificado(vet):
        raise ExpedienteError("El veterinario no tiene verificación vigente")
    return AutorizacionExpediente.objects.create(
        mascota=mascota,
        veterinario=vet,
        usuario_otorgante_id=usuario_otorgante_id,
        fecha_expiracion=timezone.now() + timedelta(hours=horas),
    )


@transaction.atomic
def regenerar_qr(*, mascota_id, usuario_creador_id, horas=24):
    if not 1 <= horas <= 720:
        raise ExpedienteError("El QR debe durar entre 1 y 720 horas")
    try:
        mascota = Mascota.objects.select_for_update().get(pk=mascota_id)
    except Mascota.DoesNotExist as exc:
        raise ExpedienteError("Mascota inexistente") from exc
    if not _custodio_puede(mascota, usuario_creador_id):
        raise ExpedienteError("El usuario no puede generar el QR")
    ahora = timezone.now()
    CodigoQRExpediente.objects.filter(
        mascota=mascota, fecha_revocacion__isnull=True, fecha_expiracion__gt=ahora
    ).update(fecha_revocacion=ahora)
    token = secrets.token_urlsafe(32)
    qr = CodigoQRExpediente.objects.create(
        mascota=mascota,
        codigo_hash=hashlib.sha256(token.encode("ascii")).hexdigest(),
        fecha_expiracion=ahora + timedelta(hours=horas),
        usuario_creador_id=usuario_creador_id,
    )
    return qr, token  # El token no vuelve a guardarse ni se muestra de nuevo.


def mascota_desde_qr(token):
    if len(token) > 100:
        raise ExpedienteError("Código QR inválido")
    huella = hashlib.sha256(token.encode("utf-8")).hexdigest()
    qr = CodigoQRExpediente.objects.select_related("mascota").filter(
        codigo_hash=huella, fecha_revocacion__isnull=True, fecha_expiracion__gt=timezone.now()
    ).first()
    if qr is None:
        raise ExpedienteError("QR inexistente, vencido o revocado")
    return qr.mascota


@transaction.atomic
def registrar_atencion(*, token_qr, usuario_veterinario_id, detalle, fecha_atencion):
    mascota_id = mascota_desde_qr(token_qr).pk
    mascota = Mascota.objects.select_for_update().get(pk=mascota_id)
    # Un cambio de titularidad puede revocar el QR mientras esperamos el bloqueo.
    mascota_desde_qr(token_qr)
    # La consulta de custodia detecta conflictos, pero el QR no autoriza.
    custodias = list(CustodiaMascota.objects.filter(mascota=mascota, fecha_fin__isnull=True)[:2])
    if len(custodias) > 1 or (custodias and mascota.dueno_id is not None):
        raise ExpedienteError("La custodia presenta un conflicto")
    try:
        vet = Veterinario.objects.select_related(
            "entidad__estado_verificacion__tipo", "usuario_profesional"
        ).get(usuario_profesional_id=usuario_veterinario_id)
    except Veterinario.DoesNotExist as exc:
        raise ExpedienteError("El usuario no es un veterinario registrado") from exc
    if not _veterinario_verificado(vet):
        raise ExpedienteError("El veterinario no está verificado")
    if not puede(usuario_veterinario_id, "expediente.escribir", objeto_id=mascota.pk):
        raise ExpedienteError("No hay permiso profesional y autorización vigente para esta mascota")
    autorizado = AutorizacionExpediente.objects.filter(
        mascota=mascota, veterinario=vet, fecha_revocacion__isnull=True,
        fecha_expiracion__gt=timezone.now(),
    ).exists()
    if not autorizado:
        raise ExpedienteError("No hay autorización vigente para esta mascota")
    if fecha_atencion > timezone.now() + timedelta(minutes=5):
        raise ExpedienteError("La atención no puede fecharse en el futuro")
    return HistorialMedico.objects.create(
        mascota=mascota, veterinario=vet, usuario_registrador_id=usuario_veterinario_id,
        detalle=detalle, fecha_atencion=fecha_atencion,
    )

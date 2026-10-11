"""Reglas transaccionales para creacion de solicitudes de adopcion."""

from django.db import transaction

from animals.models import CustodiaMascota, Mascota
from core.models import ValorMaestro

from .models import HistorialEstadoAdopcion, SolicitudAdopcion


class AdopcionError(ValueError):
    pass


def valor(tipo, nombre):
    try:
        return ValorMaestro.objects.get(tipo__nombre=tipo, nombre=nombre)
    except ValorMaestro.DoesNotExist as exc:
        raise AdopcionError(f"Falta el catalogo {tipo}: {nombre}") from exc


def _custodia_activa(mascota_id):
    custodias = list(
        CustodiaMascota.objects.select_for_update()
        .select_related("fundacion__entidad")
        .filter(mascota_id=mascota_id, fecha_fin__isnull=True)[:2]
    )
    if len(custodias) != 1:
        raise AdopcionError("La mascota debe tener una sola custodia activa")
    return custodias[0]


@transaction.atomic
def crear_solicitud_adopcion(*, mascota_id, usuario_id, observacion_solicitante="", archivo_soporte=None):
    try:
        mascota = Mascota.objects.select_for_update().select_related("estado_mascota__tipo").get(pk=mascota_id)
    except Mascota.DoesNotExist as exc:
        raise AdopcionError("Mascota inexistente") from exc
    if mascota.dueno_id == usuario_id:
        raise AdopcionError("No puede solicitar adoptar una mascota propia")
    estado_mascota = mascota.estado_mascota
    if estado_mascota.tipo.nombre != "estado_mascota" or estado_mascota.nombre != "En adopción":
        raise AdopcionError("La mascota no esta disponible para adopcion")
    custodia = _custodia_activa(mascota.pk)
    estado_pendiente = valor("estado_solicitud_adopcion", "Pendiente")
    if SolicitudAdopcion.objects.filter(
        mascota=mascota,
        usuario_solicitante_id=usuario_id,
        estado_solicitud=estado_pendiente,
    ).exists():
        raise AdopcionError("Ya existe una solicitud pendiente para esta mascota")
    if SolicitudAdopcion.objects.filter(
        mascota=mascota,
        estado_solicitud=valor("estado_solicitud_adopcion", "Aprobada"),
    ).exists():
        raise AdopcionError("La mascota ya tiene una solicitud aprobada")
    solicitud = SolicitudAdopcion.objects.create(
        mascota=mascota,
        fundacion=custodia.fundacion,
        usuario_solicitante_id=usuario_id,
        estado_solicitud=estado_pendiente,
        archivo_soporte=archivo_soporte,
        observacion_solicitante=observacion_solicitante.strip(),
    )
    HistorialEstadoAdopcion.objects.create(
        solicitud=solicitud,
        estado_nuevo=estado_pendiente,
        usuario_actor_id=usuario_id,
        observacion="Creacion de la solicitud",
    )
    return solicitud

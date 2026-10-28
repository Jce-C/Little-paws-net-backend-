"""Operaciones transaccionales del proceso de rescate.

No invocar `CasoRescate.objects.create()` desde una vista/API: el servicio
concentra las comprobaciones de permiso, cobertura, capacidad y auditoría.
"""

from django.db import connection, transaction
from django.utils import timezone
from seguridad.autorizacion import exigir

from core.models import (
    CapacidadFundacion, EntidadMiembroRol, Fundacion, Rol, ValorMaestro,
)
from .models import CasoRescate, HistorialEstadoCaso, HistorialEstadoReporte, Reporte


class ReglaNegocioError(ValueError):
    """La operación no satisface una regla del proceso."""


def _valor(tipo, nombre):
    try:
        return ValorMaestro.objects.get(tipo__nombre=tipo, nombre=nombre)
    except ValorMaestro.DoesNotExist as exc:
        raise ReglaNegocioError(f"Falta el catálogo {tipo}: {nombre}") from exc


def _fundacion_tiene_cobertura(fundacion_id, reporte_id):
    # El nombre de las columnas generadas está fijado en geography.0002.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM `FundacionZona` fz
            JOIN `ZonaGeografica` zg ON zg.`id_zona` = fz.`id_zona`
            JOIN `ReporteUbicacion` ru ON ru.`id_reporte` = %s
            WHERE fz.`id_fundacion` = %s
              AND fz.`activo` = 1
              AND ST_Intersects(zg.`geometria`, ru.`punto`) = 1
            LIMIT 1
            """,
            [reporte_id, fundacion_id],
        )
        return cursor.fetchone() is not None


@transaction.atomic
def aceptar_reporte(*, reporte_id, fundacion_id, usuario_actor_id, justificacion_sin_cupo=""):
    """Acepta un reporte pendiente, sin asignación automática de fundación.

    La fundación, la capacidad y el reporte quedan bloqueados hasta registrar
    caso e historiales. La excepción de cupo lleno exige justificación.
    """
    try:
        reporte = Reporte.objects.select_for_update().select_related("estado_reporte__tipo").get(
            pk=reporte_id
        )
        fundacion = Fundacion.objects.select_related("entidad__estado_verificacion__tipo").get(
            pk=fundacion_id
        )
        capacidad = CapacidadFundacion.objects.select_for_update().get(fundacion=fundacion)
    except (Reporte.DoesNotExist, Fundacion.DoesNotExist, CapacidadFundacion.DoesNotExist) as exc:
        raise ReglaNegocioError("Reporte, fundación o capacidad inexistente") from exc

    if reporte.estado_reporte.tipo.nombre != "estado_reporte" or reporte.estado_reporte.nombre != "Pendiente":
        raise ReglaNegocioError("Solo se puede aceptar un reporte pendiente")
    verificacion = fundacion.entidad.estado_verificacion
    if verificacion.tipo.nombre != "estado_verificacion" or verificacion.nombre != "Verificada":
        raise ReglaNegocioError("La fundación debe estar verificada")
    exigir(usuario_actor_id, "caso.aceptar", entidad_id=fundacion.entidad_id)
    if not _fundacion_tiene_cobertura(fundacion_id, reporte_id):
        raise ReglaNegocioError("El reporte está fuera de la cobertura geográfica declarada")
    if capacidad.cupos_ocupados >= capacidad.cupos_totales and not justificacion_sin_cupo.strip():
        raise ReglaNegocioError("Sin cupos disponibles: registre una justificación de emergencia")
    if CasoRescate.objects.filter(reporte=reporte).exists():
        raise ReglaNegocioError("Este reporte ya tiene un caso de rescate")

    estado_caso = _valor("estado_caso", "En atención")
    estado_reporte = _valor("estado_reporte", "En atención")
    caso = CasoRescate.objects.create(
        reporte=reporte,
        fundacion=fundacion,
        estado_caso=estado_caso,
        justificacion_sin_cupo=justificacion_sin_cupo.strip(),
        usuario_ultimo_cambio_id=usuario_actor_id,
    )
    HistorialEstadoCaso.objects.create(
        caso=caso, estado_anterior=None, estado_nuevo=estado_caso,
        usuario_actor_id=usuario_actor_id,
        observacion="Aceptación voluntaria de la fundación",
    )
    estado_anterior = reporte.estado_reporte
    reporte.estado_reporte = estado_reporte
    reporte.fecha_actualizacion = timezone.now()
    reporte.save(update_fields=["estado_reporte", "fecha_actualizacion"])
    HistorialEstadoReporte.objects.create(
        reporte=reporte, estado_anterior=estado_anterior, estado_nuevo=estado_reporte,
        usuario_actor_id=usuario_actor_id,
        observacion="Reporte aceptado como caso de rescate",
    )
    return caso

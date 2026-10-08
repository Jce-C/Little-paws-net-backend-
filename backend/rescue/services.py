"""Reglas transaccionales de aceptación y cierre de casos."""

from django.db import connection, transaction
from django.utils import timezone

from core.models import CapacidadFundacion, EntidadMiembroRol, Fundacion, Rol, ValorMaestro

from .models import CasoRescate, HistorialEstadoCaso, HistorialEstadoReporte, Reporte


class ReglaNegocioError(ValueError):
    pass


def valor(tipo, nombre):
    try:
        return ValorMaestro.objects.get(tipo__nombre=tipo, nombre=nombre)
    except ValorMaestro.DoesNotExist as exc:
        raise ReglaNegocioError(f"Falta el catálogo {tipo}: {nombre}") from exc


def miembro_puede(entidad_id, usuario_id, permiso):
    return EntidadMiembroRol.objects.filter(
        miembro__entidad_id=entidad_id,
        miembro__usuario_id=usuario_id,
        miembro__usuario__is_active=True,
        miembro__fecha_salida__isnull=True,
        rol__ambito=Rol.Ambito.ENTIDAD,
        rol__rolpermiso__permiso__codigo=permiso,
    ).exists()


def fundacion_cubre_reporte(fundacion_id, reporte_id):
    if connection.vendor != "mysql":
        return False
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM `FundacionZona` fz "
            "JOIN `ZonaGeografica` zg ON zg.`id_zona` = fz.`id_zona` "
            "JOIN `ReporteUbicacion` ru ON ru.`id_reporte` = %s "
            "WHERE fz.`id_fundacion` = %s AND fz.`activo` = 1 "
            "AND ST_Intersects(zg.`geometria`, ru.`punto`) = 1 LIMIT 1",
            [reporte_id, fundacion_id],
        )
        return cursor.fetchone() is not None


@transaction.atomic
def aceptar_reporte(*, reporte_id, fundacion_id, usuario_actor_id, justificacion_sin_cupo=""):
    try:
        reporte = Reporte.objects.select_for_update().select_related("estado_reporte__tipo").get(pk=reporte_id)
        fundacion = Fundacion.objects.select_related("entidad__estado_verificacion__tipo").get(pk=fundacion_id)
        capacidad = CapacidadFundacion.objects.select_for_update().get(fundacion=fundacion)
    except (Reporte.DoesNotExist, Fundacion.DoesNotExist, CapacidadFundacion.DoesNotExist) as exc:
        raise ReglaNegocioError("Reporte, fundación o capacidad inexistente") from exc
    if reporte.estado_reporte.tipo.nombre != "estado_reporte" or reporte.estado_reporte.nombre != "Pendiente":
        raise ReglaNegocioError("Solo se puede aceptar un reporte pendiente")
    if CasoRescate.objects.filter(reporte=reporte).exists():
        raise ReglaNegocioError("Este reporte ya tiene caso")
    verificacion = fundacion.entidad.estado_verificacion
    if verificacion.tipo.nombre != "estado_verificacion" or verificacion.nombre != "Verificada":
        raise ReglaNegocioError("La fundación debe estar verificada")
    if not miembro_puede(fundacion_id, usuario_actor_id, "caso.aceptar"):
        raise ReglaNegocioError("El usuario no puede aceptar casos por esta fundación")
    if not fundacion_cubre_reporte(fundacion_id, reporte_id):
        raise ReglaNegocioError("El reporte está fuera de la cobertura de la fundación")
    ocupa_cupo = capacidad.cupos_ocupados < capacidad.cupos_totales
    if not ocupa_cupo and not justificacion_sin_cupo.strip():
        raise ReglaNegocioError("Sin cupos: se requiere justificación de emergencia")
    estado_caso = valor("estado_caso", "En atención")
    caso = CasoRescate.objects.create(
        reporte=reporte, fundacion=fundacion, estado_caso=estado_caso,
        usuario_ultimo_cambio_id=usuario_actor_id,
        justificacion_sin_cupo=justificacion_sin_cupo.strip(), ocupa_cupo=ocupa_cupo,
    )
    if ocupa_cupo:
        capacidad.cupos_ocupados += 1
        capacidad.save(update_fields=["cupos_ocupados", "fecha_actualizacion"])
    HistorialEstadoCaso.objects.create(
        caso=caso, estado_nuevo=estado_caso, usuario_actor_id=usuario_actor_id,
        observacion="Aceptación voluntaria de la fundación",
    )
    anterior = reporte.estado_reporte
    reporte.estado_reporte = valor("estado_reporte", "En atención")
    reporte.save(update_fields=["estado_reporte", "fecha_actualizacion"])
    HistorialEstadoReporte.objects.create(
        reporte=reporte, estado_anterior=anterior, estado_nuevo=reporte.estado_reporte,
        usuario_actor_id=usuario_actor_id, observacion="Reporte aceptado como caso de rescate",
    )
    return caso


@transaction.atomic
def cerrar_caso(*, caso_id, usuario_actor_id, nuevo_estado, observacion=""):
    if nuevo_estado not in ("Cerrado", "Cancelado"):
        raise ReglaNegocioError("Transición de estado no permitida")
    try:
        caso = CasoRescate.objects.select_for_update().select_related("estado_caso").get(pk=caso_id)
        capacidad = CapacidadFundacion.objects.select_for_update().get(fundacion=caso.fundacion)
    except (CasoRescate.DoesNotExist, CapacidadFundacion.DoesNotExist) as exc:
        raise ReglaNegocioError("Caso o capacidad inexistente") from exc
    if caso.estado_caso.nombre != "En atención":
        raise ReglaNegocioError("El caso ya no está en atención")
    if not miembro_puede(caso.fundacion_id, usuario_actor_id, "caso.cambiar_estado"):
        raise ReglaNegocioError("El usuario no puede cambiar este caso")
    anterior = caso.estado_caso
    caso.estado_caso = valor("estado_caso", nuevo_estado)
    caso.fecha_cierre = timezone.now()
    caso.usuario_ultimo_cambio_id = usuario_actor_id
    caso.observaciones = observacion.strip()
    caso.save(update_fields=["estado_caso", "fecha_cierre", "usuario_ultimo_cambio", "observaciones"])
    if caso.ocupa_cupo:
        capacidad.cupos_ocupados -= 1
        capacidad.save(update_fields=["cupos_ocupados", "fecha_actualizacion"])
    HistorialEstadoCaso.objects.create(
        caso=caso, estado_anterior=anterior, estado_nuevo=caso.estado_caso,
        usuario_actor_id=usuario_actor_id, observacion=observacion.strip(),
    )
    reporte = Reporte.objects.select_for_update().get(pk=caso.reporte_id)
    anterior_reporte = reporte.estado_reporte
    reporte.estado_reporte = valor("estado_reporte", "Cerrado")
    reporte.save(update_fields=["estado_reporte", "fecha_actualizacion"])
    HistorialEstadoReporte.objects.create(
        reporte=reporte, estado_anterior=anterior_reporte, estado_nuevo=reporte.estado_reporte,
        usuario_actor_id=usuario_actor_id, observacion=f"Cierre del caso: {nuevo_estado}",
    )
    return caso

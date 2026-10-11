"""Reglas transaccionales de solicitudes y resoluciones de adopción."""

from django.db import transaction
from django.utils import timezone

from animals.models import CustodiaMascota, Mascota
from core.models import EntidadMiembroRol, Rol, UsuarioRol, ValorMaestro

from .models import HistorialEstadoAdopcion, SolicitudAdopcion


class AdopcionError(ValueError):
    pass


class AdopcionPermisoError(AdopcionError):
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


def _admin_puede_resolver(usuario_id):
    return UsuarioRol.objects.filter(
        usuario_id=usuario_id,
        usuario__is_active=True,
        fecha_revocacion__isnull=True,
        rol__codigo="ADMIN_PLATAFORMA",
        rol__ambito=Rol.Ambito.GLOBAL,
        rol__rolpermiso__permiso__codigo="adopcion.resolver",
    ).exists()


def _gestor_puede_resolver(entidad_id, usuario_id):
    return EntidadMiembroRol.objects.filter(
        miembro__entidad_id=entidad_id,
        miembro__usuario_id=usuario_id,
        miembro__usuario__is_active=True,
        miembro__fecha_salida__isnull=True,
        rol__codigo="GESTOR_FUNDACION",
        rol__ambito=Rol.Ambito.ENTIDAD,
        rol__rolpermiso__permiso__codigo="adopcion.resolver",
    ).exists()


@transaction.atomic
def crear_solicitud_adopcion(*, mascota_id, usuario_id, observaciones=""):
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
    verificacion = custodia.fundacion.entidad.estado_verificacion
    if verificacion.tipo.nombre != "estado_verificacion" or verificacion.nombre != "Verificada":
        raise AdopcionError("La fundación custodiante debe estar verificada")
    estado_pendiente = valor("estado_solicitud_adopcion", "Pendiente")
    if SolicitudAdopcion.objects.filter(
        mascota=mascota,
        usuario_adoptante_id=usuario_id,
        estado_adopcion=estado_pendiente,
    ).exists():
        raise AdopcionError("Ya existe una solicitud pendiente para esta mascota")
    if SolicitudAdopcion.objects.filter(
        mascota=mascota,
        estado_adopcion=valor("estado_solicitud_adopcion", "Aprobada"),
    ).exists():
        raise AdopcionError("La mascota ya tiene una solicitud aprobada")
    solicitud = SolicitudAdopcion.objects.create(
        mascota=mascota,
        usuario_adoptante_id=usuario_id,
        estado_adopcion=estado_pendiente,
        observaciones=observaciones.strip(),
    )
    HistorialEstadoAdopcion.objects.create(
        solicitud=solicitud,
        estado_nuevo=estado_pendiente,
        usuario_actor_id=usuario_id,
        observacion="Creacion de la solicitud",
    )
    return solicitud


@transaction.atomic
def resolver_solicitud_adopcion(*, solicitud_id, usuario_actor_id, estado, observacion):
    if estado not in ("Aprobada", "Rechazada"):
        raise AdopcionError("La decisión debe ser Aprobada o Rechazada")
    observacion = observacion.strip()
    if not observacion:
        raise AdopcionError("La resolución requiere una observación")

    # Se bloquea primero la mascota, igual que al crear una solicitud, para
    # serializar nuevas solicitudes y resoluciones concurrentes.
    mascota_id = SolicitudAdopcion.objects.filter(pk=solicitud_id).values_list("mascota_id", flat=True).first()
    if mascota_id is None:
        raise AdopcionError("Solicitud inexistente")
    mascota = Mascota.objects.select_for_update().select_related("estado_mascota__tipo").get(pk=mascota_id)
    solicitud = SolicitudAdopcion.objects.select_for_update().select_related(
        "estado_adopcion__tipo"
    ).get(pk=solicitud_id)
    if solicitud.estado_adopcion.tipo.nombre != "estado_solicitud_adopcion" or solicitud.estado_adopcion.nombre != "Pendiente":
        raise AdopcionError("Solo se puede resolver una solicitud pendiente")
    if solicitud.usuario_adoptante_id == usuario_actor_id:
        raise AdopcionPermisoError("El solicitante no puede resolver su propia solicitud")
    custodia = _custodia_activa(mascota.pk)
    verificacion = custodia.fundacion.entidad.estado_verificacion
    if verificacion.tipo.nombre != "estado_verificacion" or verificacion.nombre != "Verificada":
        raise AdopcionError("La fundación custodiante debe estar verificada")
    if not (
        _gestor_puede_resolver(custodia.fundacion_id, usuario_actor_id)
        or _admin_puede_resolver(usuario_actor_id)
    ):
        raise AdopcionPermisoError("No tiene permiso para resolver esta solicitud")
    if mascota.estado_mascota.tipo.nombre != "estado_mascota" or mascota.estado_mascota.nombre != "En adopción":
        raise AdopcionError("La mascota ya no está disponible para adopción")

    anterior = solicitud.estado_adopcion
    solicitud.estado_adopcion = valor("estado_solicitud_adopcion", estado)
    solicitud.save(update_fields=["estado_adopcion"])
    HistorialEstadoAdopcion.objects.create(
        solicitud=solicitud,
        estado_anterior=anterior,
        estado_nuevo=solicitud.estado_adopcion,
        usuario_actor_id=usuario_actor_id,
        observacion=observacion,
    )
    if estado == "Aprobada":
        pendientes = SolicitudAdopcion.objects.select_for_update().filter(
            mascota=mascota,
            estado_adopcion=anterior,
        ).exclude(pk=solicitud.pk)
        cancelada = valor("estado_solicitud_adopcion", "Cancelada")
        for otra in pendientes:
            otra.estado_adopcion = cancelada
            otra.save(update_fields=["estado_adopcion"])
            HistorialEstadoAdopcion.objects.create(
                solicitud=otra,
                estado_anterior=anterior,
                estado_nuevo=cancelada,
                usuario_actor_id=usuario_actor_id,
                observacion=f"Cierre automático por aprobación de solicitud {solicitud.pk}",
            )
        mascota.dueno_id = solicitud.usuario_adoptante_id
        mascota.estado_mascota = valor("estado_mascota", "Adoptada")
        mascota.save(update_fields=["dueno", "estado_mascota"])
        custodia.fecha_fin = timezone.now()
        custodia.save(update_fields=["fecha_fin"])
    return solicitud

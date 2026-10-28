"""Resolución atómica de solicitudes de adopción bajo custodia vigente."""

from django.db import transaction
from django.utils import timezone
from seguridad.autorizacion import exigir

from animals.models import CustodiaMascota, Mascota
from core.models import EntidadMiembroRol, Notificacion, Rol, ValorMaestro
from .models import HistorialEstadoAdopcion, SolicitudAdopcion


class AdopcionError(ValueError):
    pass


def _valor(tipo, nombre):
    return ValorMaestro.objects.get(tipo__nombre=tipo, nombre=nombre)


@transaction.atomic
def resolver_solicitud(*, solicitud_id, fundacion_id, usuario_actor_id, aprobar, observacion=""):
    try:
        mascota_id = SolicitudAdopcion.objects.values_list("mascota_id", flat=True).get(pk=solicitud_id)
    except SolicitudAdopcion.DoesNotExist as exc:
        raise AdopcionError("Solicitud inexistente") from exc
    # Bloqueo de mascota primero: dos solicitudes de la misma mascota no pueden
    # aprobarse simultáneamente ni invertir el orden de bloqueos.
    mascota = Mascota.objects.select_for_update().get(pk=mascota_id)
    solicitud = SolicitudAdopcion.objects.select_for_update().select_related("estado_adopcion").get(
        pk=solicitud_id
    )
    if solicitud.estado_adopcion != _valor("estado_adopcion", "Pendiente"):
        raise AdopcionError("La solicitud ya fue resuelta")
    custodia = CustodiaMascota.objects.select_for_update().filter(
        mascota=mascota, fundacion_id=fundacion_id, fecha_fin__isnull=True
    ).first()
    if custodia is None:
        raise AdopcionError("La fundación no tiene la custodia vigente")
    if custodia.fundacion.entidad.estado_verificacion.nombre != "Verificada":
        raise AdopcionError("La fundación no está verificada")
    exigir(usuario_actor_id, "adopcion.resolver", entidad_id=fundacion_id, objeto_id=solicitud_id)
    if solicitud.usuario_adoptante_id == usuario_actor_id:
        raise AdopcionError("No puedes resolver tu propia solicitud de adopción")
    if aprobar and mascota.estado_mascota != _valor("estado_mascota", "En adopción"):
        raise AdopcionError("La mascota no está disponible para adopción")

    ahora = timezone.now()
    nuevo_estado = _valor("estado_adopcion", "Aprobada" if aprobar else "Rechazada")
    solicitud.estado_adopcion = nuevo_estado
    solicitud.fecha_resolucion = ahora
    solicitud.observaciones = observacion
    solicitud.save(update_fields=["estado_adopcion", "fecha_resolucion", "observaciones"])
    HistorialEstadoAdopcion.objects.create(
        solicitud=solicitud,
        estado_anterior=_valor("estado_adopcion", "Pendiente"),
        estado_nuevo=nuevo_estado,
        usuario_actor_id=usuario_actor_id,
        observacion=observacion,
    )
    tipo_notificacion = _valor("tipo_notificacion", "Resultado de adopción")
    Notificacion.objects.create(
        usuario=solicitud.usuario_adoptante,
        tipo_notificacion=tipo_notificacion,
        contenido=f"Tu solicitud de adopción {solicitud.pk} fue {nuevo_estado.nombre.lower()}.",
    )
    if aprobar:
        mascota.estado_mascota = _valor("estado_mascota", "Adoptada")
        mascota.dueno = solicitud.usuario_adoptante
        mascota.save(update_fields=["estado_mascota", "dueno"])
        custodia.fecha_fin = ahora
        custodia.save(update_fields=["fecha_fin"])
        otras = list(SolicitudAdopcion.objects.select_for_update().filter(
            mascota=mascota, estado_adopcion=_valor("estado_adopcion", "Pendiente")
        ).exclude(pk=solicitud.pk))
        estado_cerrado = _valor("estado_adopcion", "Cerrada por adopción")
        for otra in otras:
            otra.estado_adopcion = estado_cerrado
            otra.fecha_resolucion = ahora
            otra.save(update_fields=["estado_adopcion", "fecha_resolucion"])
            HistorialEstadoAdopcion.objects.create(
                solicitud=otra,
                estado_anterior=_valor("estado_adopcion", "Pendiente"),
                estado_nuevo=estado_cerrado,
                usuario_actor_id=usuario_actor_id,
                observacion="Cierre por adopción aprobada de la mascota",
            )
            Notificacion.objects.create(
                usuario=otra.usuario_adoptante,
                tipo_notificacion=tipo_notificacion,
                contenido=f"La solicitud {otra.pk} se cerró porque la mascota fue adoptada.",
            )
    return solicitud

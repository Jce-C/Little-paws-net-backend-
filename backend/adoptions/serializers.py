"""Validacion y representacion de solicitudes de adopcion."""

from rest_framework import serializers

from core.models import ArchivoDigital


class SolicitudAdopcionCrearSerializer(serializers.Serializer):
    id_mascota = serializers.IntegerField(min_value=1)
    id_archivo_soporte = serializers.PrimaryKeyRelatedField(
        queryset=ArchivoDigital.objects.all(),
        required=False,
        allow_null=True,
        source="archivo_soporte",
    )
    observacion_solicitante = serializers.CharField(
        max_length=5000,
        required=False,
        allow_blank=True,
    )


def representar_solicitud(solicitud, incluir_historial=False):
    datos = {
        "id_solicitud_adopcion": solicitud.pk,
        "id_mascota": solicitud.mascota_id,
        "mascota": solicitud.mascota.nombre,
        "id_fundacion": solicitud.fundacion_id,
        "fundacion": solicitud.fundacion.entidad.nombre,
        "id_usuario_solicitante": solicitud.usuario_solicitante_id,
        "estado": solicitud.estado_solicitud.nombre,
        "fecha_solicitud": solicitud.fecha_solicitud,
        "fecha_resolucion": solicitud.fecha_resolucion,
        "id_usuario_resolutor": solicitud.usuario_resolutor_id,
        "observacion_solicitante": solicitud.observacion_solicitante,
        "observacion_resolucion": solicitud.observacion_resolucion,
        "id_archivo_soporte": solicitud.archivo_soporte_id,
    }
    if incluir_historial:
        datos["historial"] = [
            {
                "id_historial_adopcion": cambio.pk,
                "estado_anterior": None if cambio.estado_anterior is None else cambio.estado_anterior.nombre,
                "estado_nuevo": cambio.estado_nuevo.nombre,
                "id_usuario_actor": cambio.usuario_actor_id,
                "fecha_cambio": cambio.fecha_cambio,
                "observacion": cambio.observacion,
            }
            for cambio in solicitud.historialestadoadopcion_set.select_related(
                "estado_anterior",
                "estado_nuevo",
            ).order_by("fecha_cambio", "pk")
        ]
    return datos

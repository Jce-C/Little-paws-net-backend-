"""Validacion y representacion de solicitudes de adopcion."""

from rest_framework import serializers

class SolicitudAdopcionCrearSerializer(serializers.Serializer):
    id_mascota = serializers.IntegerField(min_value=1)
    observaciones = serializers.CharField(
        max_length=5000,
        required=False,
        allow_blank=True,
    )


class ResolverSolicitudAdopcionSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=("Aprobada", "Rechazada"))
    observacion = serializers.CharField(max_length=5000, allow_blank=False, trim_whitespace=True)


def representar_solicitud(solicitud, incluir_historial=False):
    datos = {
        "id_solicitud_adopcion": solicitud.pk,
        "id_mascota": solicitud.mascota_id,
        "mascota": solicitud.mascota.nombre,
        "id_usuario_adoptante": solicitud.usuario_adoptante_id,
        "estado": solicitud.estado_adopcion.nombre,
        "fecha_solicitud": solicitud.fecha_solicitud,
        "observaciones": solicitud.observaciones,
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

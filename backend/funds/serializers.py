"""Entrada validada y salida pública del catálogo de fondos externos."""

from decimal import Decimal

from rest_framework import serializers

from .models import FondoExterno


class FondoExternoCrearSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150, allow_blank=False, trim_whitespace=True)
    instrucciones_transferencia = serializers.CharField(
        max_length=2000, allow_blank=False, trim_whitespace=True,
    )


def representar_fondo(fondo):
    return {"id_fondo_externo": fondo.pk, "nombre": fondo.nombre}


class CompromisoDonacionCrearSerializer(serializers.Serializer):
    id_fondo_externo = serializers.PrimaryKeyRelatedField(
        queryset=FondoExterno.objects.all(), source="fondo_externo",
    )
    monto_comprometido = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01"),
    )


def representar_donacion(donacion, *, incluir_historial=False):
    datos = {
        "id_donacion": donacion.pk,
        "id_fondo_externo": donacion.fondo_externo_id,
        "fondo": donacion.fondo_externo.nombre,
        "id_usuario_donante": donacion.usuario_donante_id,
        "estado": donacion.estado_donacion.nombre,
        "monto_comprometido": str(donacion.monto_comprometido),
        "fecha_compromiso": donacion.fecha_compromiso,
        "aviso": "Compromiso registrado; no acredita recepción de dinero",
    }
    if incluir_historial:
        datos["historial"] = [
            {
                "id_historial_donacion": cambio.pk,
                "estado_anterior": None if cambio.estado_anterior_id is None else cambio.estado_anterior.nombre,
                "estado_nuevo": cambio.estado_nuevo.nombre,
                "id_usuario_actor": cambio.usuario_actor_id,
                "fecha_cambio": cambio.fecha_cambio,
                "observacion": cambio.observacion,
            }
            for cambio in donacion.historialestadodonacion_set.select_related(
                "estado_anterior", "estado_nuevo",
            ).order_by("fecha_cambio", "pk")
        ]
    return datos

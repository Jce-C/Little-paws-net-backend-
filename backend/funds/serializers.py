"""Entrada validada y salida pública del catálogo de fondos externos."""

from rest_framework import serializers


class FondoExternoCrearSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150, allow_blank=False, trim_whitespace=True)
    instrucciones_transferencia = serializers.CharField(
        max_length=2000, allow_blank=False, trim_whitespace=True,
    )


def representar_fondo(fondo):
    return {"id_fondo_externo": fondo.pk, "nombre": fondo.nombre}

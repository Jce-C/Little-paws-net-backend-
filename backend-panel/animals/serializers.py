"""Entradas validadas para la autorización y el expediente."""

from rest_framework import serializers


class AutorizarSerializer(serializers.Serializer):
    id_veterinario = serializers.IntegerField(min_value=1)
    horas = serializers.IntegerField(min_value=1, max_value=720, default=24)


class AtencionSerializer(serializers.Serializer):
    detalle = serializers.CharField(max_length=10000)
    fecha_atencion = serializers.DateTimeField()

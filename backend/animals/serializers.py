"""Entradas de custodia y expediente médico."""

from rest_framework import serializers


class AutorizarVeterinarioSerializer(serializers.Serializer):
    id_veterinario = serializers.IntegerField(min_value=1)
    dias = serializers.IntegerField(min_value=1, max_value=30, default=7)


class RegenerarQRSerializer(serializers.Serializer):
    horas = serializers.IntegerField(min_value=1, max_value=72, default=24)


class AccesoQRSerializer(serializers.Serializer):
    codigo_qr = serializers.CharField(min_length=32, max_length=128, write_only=True)


class AtencionSerializer(AccesoQRSerializer):
    detalle = serializers.CharField(max_length=10000)
    fecha_atencion = serializers.DateTimeField()


class AtencionExternaSerializer(serializers.Serializer):
    nombre_veterinario_externo = serializers.CharField(max_length=150)
    registro_profesional_externo = serializers.CharField(max_length=80)
    detalle = serializers.CharField(max_length=10000)
    fecha_atencion = serializers.DateTimeField()

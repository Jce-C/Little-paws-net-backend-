"""Entradas de custodia y expediente médico."""

from rest_framework import serializers
from django.utils import timezone

from core.models import ValorMaestro

from .models import Raza


class MascotaCasoSerializer(serializers.Serializer):
    raza = serializers.PrimaryKeyRelatedField(queryset=Raza.objects.all())
    nombre = serializers.CharField(max_length=120, required=False, allow_blank=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    es_estimada = serializers.BooleanField(default=False)
    sexo = serializers.PrimaryKeyRelatedField(queryset=ValorMaestro.objects.all(), required=False, allow_null=True)
    tamano = serializers.PrimaryKeyRelatedField(queryset=ValorMaestro.objects.all(), required=False, allow_null=True)

    def validate(self, attrs):
        fecha = attrs.get("fecha_nacimiento")
        if attrs.get("es_estimada") and fecha is None:
            raise serializers.ValidationError("Una fecha estimada requiere fecha_nacimiento")
        if fecha and fecha > timezone.localdate():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura")
        for campo, tipo in (("sexo", "sexo_mascota"), ("tamano", "tamano_mascota")):
            valor = attrs.get(campo)
            if valor is not None and valor.tipo.nombre != tipo:
                raise serializers.ValidationError({campo: "Valor de catálogo incorrecto"})
        return attrs


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

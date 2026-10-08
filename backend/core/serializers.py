"""Representación pública de los catálogos de referencia."""

from rest_framework import serializers

from .models import TipoMaestro, ValorMaestro


class ValorMaestroSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValorMaestro
        fields = ("id_valor_maestro", "nombre")


class TipoMaestroSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source="nombre")
    valores = ValorMaestroSerializer(source="valormaestro_set", many=True)

    class Meta:
        model = TipoMaestro
        fields = ("tipo", "valores")

"""Representación pública de los catálogos de referencia."""

from rest_framework import serializers

from .models import TipoMaestro, ValorMaestro
from .i18n import etiqueta


class ValorMaestroSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()

    def get_nombre(self, obj):
        return etiqueta(obj.nombre)

    class Meta:
        model = ValorMaestro
        fields = ("id_valor_maestro", "nombre")


class TipoMaestroSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source="nombre")
    valores = ValorMaestroSerializer(source="valormaestro_set", many=True)

    class Meta:
        model = TipoMaestro
        fields = ("tipo", "valores")

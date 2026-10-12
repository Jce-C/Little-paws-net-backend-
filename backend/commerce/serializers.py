"""Entradas acotadas y salida JSON del catálogo comercial."""

from decimal import Decimal

from rest_framework import serializers

from core.models import Tienda, ValorMaestro


class ProductoCrearSerializer(serializers.Serializer):
    id_tienda = serializers.PrimaryKeyRelatedField(queryset=Tienda.objects.all(), source="tienda")
    id_categoria_producto = serializers.PrimaryKeyRelatedField(
        queryset=ValorMaestro.objects.filter(tipo__nombre="categoria_producto"), source="categoria_producto",
    )
    id_tipo_producto = serializers.PrimaryKeyRelatedField(
        queryset=ValorMaestro.objects.filter(tipo__nombre="tipo_producto"), source="tipo_producto",
    )
    nombre = serializers.CharField(max_length=150, allow_blank=False, trim_whitespace=True)
    descripcion = serializers.CharField(max_length=4000, allow_blank=True, required=False, trim_whitespace=True)
    precio = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    existencias = serializers.IntegerField(min_value=0)
    destacado = serializers.BooleanField(required=False, default=False)


class ProductoActualizarSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150, allow_blank=False, trim_whitespace=True, required=False)
    descripcion = serializers.CharField(max_length=4000, allow_blank=True, trim_whitespace=True, required=False)
    precio = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01"), required=False,
    )
    existencias = serializers.IntegerField(min_value=0, required=False)
    destacado = serializers.BooleanField(required=False)
    id_categoria_producto = serializers.PrimaryKeyRelatedField(
        queryset=ValorMaestro.objects.filter(tipo__nombre="categoria_producto"),
        source="categoria_producto", required=False,
    )
    id_tipo_producto = serializers.PrimaryKeyRelatedField(
        queryset=ValorMaestro.objects.filter(tipo__nombre="tipo_producto"),
        source="tipo_producto", required=False,
    )
    id_estado_producto = serializers.PrimaryKeyRelatedField(
        queryset=ValorMaestro.objects.filter(tipo__nombre="estado_producto"),
        source="estado_producto", required=False,
    )

    def validate(self, attrs):
        desconocidos = set(self.initial_data) - set(self.fields)
        if desconocidos:
            raise serializers.ValidationError({campo: "Campo no modificable" for campo in desconocidos})
        if not attrs:
            raise serializers.ValidationError("Indique al menos un campo para actualizar")
        return attrs


def representar_producto(producto):
    return {
        "id_producto": producto.pk,
        "id_tienda": producto.tienda_id,
        "tienda": producto.tienda.entidad.nombre,
        "id_categoria_producto": producto.categoria_producto_id,
        "categoria": producto.categoria_producto.nombre,
        "id_tipo_producto": producto.tipo_producto_id,
        "tipo": producto.tipo_producto.nombre,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": str(producto.precio),
        "existencias": producto.existencias,
        "destacado": producto.destacado,
        "estado": producto.estado_producto.nombre,
    }

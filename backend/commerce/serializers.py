"""Entradas acotadas y salida JSON del catálogo comercial."""

from decimal import Decimal

from rest_framework import serializers

from core.models import Anunciante, ArchivoDigital, Tienda, ValorMaestro

from .models import Producto
from .i18n import etiqueta, ingles_activo, texto


class ProductoCrearSerializer(serializers.Serializer):
    id_tienda = serializers.PrimaryKeyRelatedField(queryset=Tienda.objects.all(), source="tienda")
    id_categoria_producto = serializers.PrimaryKeyRelatedField(
        queryset=ValorMaestro.objects.filter(tipo__nombre="categoria_producto"), source="categoria_producto",
    )
    id_tipo_producto = serializers.PrimaryKeyRelatedField(
        queryset=ValorMaestro.objects.filter(tipo__nombre="tipo_producto"), source="tipo_producto",
    )
    nombre = serializers.CharField(max_length=150, allow_blank=False, trim_whitespace=True)
    nombre_en = serializers.CharField(max_length=150, allow_blank=True, required=False, trim_whitespace=True)
    descripcion = serializers.CharField(max_length=4000, allow_blank=True, required=False, trim_whitespace=True)
    descripcion_en = serializers.CharField(max_length=4000, allow_blank=True, required=False, trim_whitespace=True)
    precio = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    existencias = serializers.IntegerField(min_value=0)
    destacado = serializers.BooleanField(required=False, default=False)


class ProductoActualizarSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150, allow_blank=False, trim_whitespace=True, required=False)
    nombre_en = serializers.CharField(max_length=150, allow_blank=True, trim_whitespace=True, required=False)
    descripcion = serializers.CharField(max_length=4000, allow_blank=True, trim_whitespace=True, required=False)
    descripcion_en = serializers.CharField(max_length=4000, allow_blank=True, trim_whitespace=True, required=False)
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
            raise serializers.ValidationError({
                campo: texto("Campo no modificable", "Field cannot be changed") for campo in desconocidos
            })
        if not attrs:
            raise serializers.ValidationError(texto(
                "Indique al menos un campo para actualizar", "Provide at least one field to update",
            ))
        return attrs


def representar_producto(producto):
    ingles = ingles_activo()
    return {
        "id_producto": producto.pk,
        "id_tienda": producto.tienda_id,
        "tienda": producto.tienda.entidad.nombre,
        "id_categoria_producto": producto.categoria_producto_id,
        "categoria": etiqueta(producto.categoria_producto.nombre),
        "id_tipo_producto": producto.tipo_producto_id,
        "tipo": etiqueta(producto.tipo_producto.nombre),
        "nombre": (producto.nombre_en or producto.nombre) if ingles else producto.nombre,
        "descripcion": (producto.descripcion_en or producto.descripcion) if ingles else producto.descripcion,
        "precio": str(producto.precio),
        "existencias": producto.existencias,
        "destacado": producto.destacado,
        "estado": etiqueta(producto.estado_producto.nombre),
    }


class DetallePedidoEntradaSerializer(serializers.Serializer):
    id_producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source="producto",
    )
    cantidad = serializers.IntegerField(min_value=1, max_value=1000)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            desconocidos = set(data) - set(self.fields)
            if desconocidos:
                raise serializers.ValidationError({
                    campo: texto("Campo no permitido", "Field not allowed") for campo in desconocidos
                })
        return super().to_internal_value(data)


class PedidoCrearSerializer(serializers.Serializer):
    id_tienda = serializers.PrimaryKeyRelatedField(queryset=Tienda.objects.all(), source="tienda")
    productos = DetallePedidoEntradaSerializer(many=True, allow_empty=False)

    def validate(self, attrs):
        desconocidos = set(self.initial_data) - set(self.fields)
        if desconocidos:
            raise serializers.ValidationError({
                campo: texto("Campo no permitido", "Field not allowed") for campo in desconocidos
            })
        return attrs

    def validate_productos(self, productos):
        if len(productos) > 50:
            raise serializers.ValidationError(texto(
                "El pedido admite como máximo 50 productos distintos",
                "The order allows at most 50 distinct products",
            ))
        ids = [item["producto"].pk for item in productos]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(texto(
                "No repita productos; indique una sola cantidad por producto",
                "Do not repeat products; provide one quantity per product",
            ))
        return productos


def representar_pedido(pedido):
    detalles = list(pedido.detallepedido_set.select_related("producto").order_by("producto_id"))
    total = sum((detalle.precio_referencia * detalle.cantidad for detalle in detalles), Decimal("0.00"))
    return {
        "id_pedido": pedido.pk,
        "id_tienda": pedido.tienda_id,
        "id_usuario_cliente": pedido.usuario_cliente_id,
        "estado": etiqueta(pedido.estado_pedido.nombre),
        "fecha_inicio": pedido.fecha_inicio,
        "productos": [
            {
                "id_producto": detalle.producto_id,
                "nombre": detalle.producto.nombre,
                "cantidad": detalle.cantidad,
                "precio_referencia": str(detalle.precio_referencia),
                "subtotal_referencia": str(detalle.precio_referencia * detalle.cantidad),
            }
            for detalle in detalles
        ],
        "total_referencial": str(total),
        "aviso": texto(
            "Pedido iniciado: no confirma pago ni reserva inventario",
            "Order started: payment is not confirmed and inventory is not reserved",
        ),
    }


class EspacioPublicitarioCrearSerializer(serializers.Serializer):
    id_anunciante = serializers.PrimaryKeyRelatedField(
        queryset=Anunciante.objects.all(), source="anunciante",
    )
    id_tipo_publicidad = serializers.PrimaryKeyRelatedField(
        queryset=ValorMaestro.objects.filter(tipo__nombre="tipo_publicidad"),
        source="tipo_publicidad",
    )
    fecha_inicio = serializers.DateTimeField()
    fecha_fin = serializers.DateTimeField()
    url_destino = serializers.URLField(max_length=2048)
    id_archivo = serializers.PrimaryKeyRelatedField(
        queryset=ArchivoDigital.objects.all(), source="archivo",
    )

    def validate(self, attrs):
        desconocidos = set(self.initial_data) - set(self.fields)
        if desconocidos:
            raise serializers.ValidationError({
                campo: texto("Campo no permitido", "Field not allowed") for campo in desconocidos
            })
        if attrs["fecha_fin"] <= attrs["fecha_inicio"]:
            raise serializers.ValidationError({
                "fecha_fin": texto("Debe ser posterior al inicio", "Must be later than the start"),
            })
        return attrs


def representar_espacio(espacio):
    return {
        "id_espacio": espacio.pk,
        "id_anunciante": espacio.anunciante_id,
        "anunciante": espacio.anunciante.entidad.nombre,
        "id_tipo_publicidad": espacio.tipo_publicidad_id,
        "tipo_publicidad": etiqueta(espacio.tipo_publicidad.nombre),
        "fecha_inicio": espacio.fecha_inicio,
        "fecha_fin": espacio.fecha_fin,
        "url_destino": espacio.url_destino,
        "id_archivo": espacio.archivo_id,
        "url_archivo": espacio.archivo.url_archivo,
        "aviso": texto(
            "Publicación informativa; Little Paws Net no procesa cobros de publicidad",
            "Informational listing; Little Paws Net does not process advertising payments",
        ),
    }


class TarifaPublicacionCrearSerializer(serializers.Serializer):
    id_tienda = serializers.PrimaryKeyRelatedField(queryset=Tienda.objects.all(), source="tienda")
    id_tipo_tarifa = serializers.PrimaryKeyRelatedField(
        queryset=ValorMaestro.objects.filter(tipo__nombre="tipo_tarifa"),
        source="tipo_tarifa",
    )
    monto = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.00"))
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    concepto = serializers.CharField(max_length=255, allow_blank=False, trim_whitespace=True)
    concepto_en = serializers.CharField(max_length=255, allow_blank=True, required=False, trim_whitespace=True)

    def validate(self, attrs):
        desconocidos = set(self.initial_data) - set(self.fields)
        if desconocidos:
            raise serializers.ValidationError({
                campo: texto("Campo no permitido", "Field not allowed") for campo in desconocidos
            })
        if attrs["fecha_fin"] < attrs["fecha_inicio"]:
            raise serializers.ValidationError({
                "fecha_fin": texto("Debe ser igual o posterior al inicio", "Must be on or after the start"),
            })
        return attrs


def representar_tarifa(tarifa):
    ingles = ingles_activo()
    return {
        "id_tarifa": tarifa.pk,
        "id_tienda": tarifa.tienda_id,
        "tienda": tarifa.tienda.entidad.nombre,
        "id_tipo_tarifa": tarifa.tipo_tarifa_id,
        "tipo_tarifa": etiqueta(tarifa.tipo_tarifa.nombre),
        "monto": str(tarifa.monto),
        "fecha_inicio": tarifa.fecha_inicio,
        "fecha_fin": tarifa.fecha_fin,
        "concepto": (tarifa.concepto_en or tarifa.concepto) if ingles else tarifa.concepto,
        "aviso": texto(
            "Tarifa informativa; no acredita cobro ni pago",
            "Informational rate; this does not confirm a charge or payment",
        ),
    }

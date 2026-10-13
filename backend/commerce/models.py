"""Catálogo, pedidos iniciados y publicidad; no registra cobros ni reserva inventario."""

from django.conf import settings
from django.db import models
from django.db.models import F, Q

from core.models import Anunciante, ArchivoDigital, Tienda, ValorMaestro


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, db_column="id_tienda")
    categoria_producto = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_categoria_producto",
        related_name="productos_categoria",
    )
    tipo_producto = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_tipo_producto",
        related_name="productos_tipo",
    )
    nombre = models.CharField(max_length=150)
    nombre_en = models.CharField(max_length=150, blank=True)
    descripcion = models.TextField(blank=True)
    descripcion_en = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    existencias = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)
    estado_producto = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_producto",
        related_name="productos_estado",
    )

    class Meta:
        db_table = "Producto"
        constraints = [
            models.CheckConstraint(condition=Q(precio__gt=0), name="ck_producto_precio_pos"),
            models.CheckConstraint(condition=Q(existencias__gte=0), name="ck_producto_existencias"),
        ]
        indexes = [
            models.Index(fields=["tienda", "estado_producto"], name="ix_producto_tienda_estado"),
            models.Index(fields=["categoria_producto", "tipo_producto"], name="ix_producto_categoria_tipo"),
        ]


class ProductoImagen(models.Model):
    archivo = models.OneToOneField(
        ArchivoDigital, on_delete=models.PROTECT, primary_key=True, db_column="id_archivo",
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column="id_producto")
    orden = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "ProductoImagen"
        constraints = [
            models.UniqueConstraint(fields=["producto", "orden"], name="uq_producto_imagen_orden"),
        ]


class PedidoIniciado(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, db_column="id_tienda")
    usuario_cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_cliente",
    )
    estado_pedido = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_pedido",
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "PedidoIniciado"
        indexes = [
            models.Index(fields=["usuario_cliente", "fecha_inicio"], name="ix_pedido_cliente_fecha"),
            models.Index(fields=["tienda", "fecha_inicio"], name="ix_pedido_tienda_fecha"),
        ]


class DetallePedido(models.Model):
    pk = models.CompositePrimaryKey("pedido_id", "producto_id")
    pedido = models.ForeignKey(PedidoIniciado, on_delete=models.PROTECT, db_column="id_pedido")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column="id_producto")
    cantidad = models.PositiveIntegerField()
    precio_referencia = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "DetallePedido"
        constraints = [
            models.CheckConstraint(condition=Q(cantidad__gt=0), name="ck_detalle_cantidad_pos"),
            models.CheckConstraint(condition=Q(precio_referencia__gte=0), name="ck_detalle_precio_no_neg"),
        ]


class EspacioPublicitario(models.Model):
    id_espacio = models.AutoField(primary_key=True)
    anunciante = models.ForeignKey(Anunciante, on_delete=models.PROTECT, db_column="id_anunciante")
    tipo_publicidad = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_tipo_publicidad",
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    url_destino = models.URLField(max_length=2048)
    archivo = models.ForeignKey(ArchivoDigital, on_delete=models.PROTECT, db_column="id_archivo")

    class Meta:
        db_table = "EspacioPublicitario"
        constraints = [
            models.CheckConstraint(condition=Q(fecha_fin__gt=F("fecha_inicio")), name="ck_espacio_fechas"),
        ]


class TarifaPublicacion(models.Model):
    id_tarifa = models.AutoField(primary_key=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, db_column="id_tienda")
    tipo_tarifa = models.ForeignKey(ValorMaestro, on_delete=models.PROTECT, db_column="id_tipo_tarifa")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    concepto = models.CharField(max_length=255)
    concepto_en = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "TarifaPublicacion"
        constraints = [
            models.CheckConstraint(condition=Q(monto__gte=0), name="ck_tarifa_monto_no_neg"),
            models.CheckConstraint(condition=Q(fecha_fin__gte=F("fecha_inicio")), name="ck_tarifa_fechas"),
        ]

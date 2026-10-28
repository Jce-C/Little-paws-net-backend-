"""Comercio, publicidad y moderación (Sally Andrea)."""

from django.conf import settings
from django.db import models
from django.db.models import F, Q

from core.models import Anunciante, ArchivoDigital, Clinica, Tienda, ValorMaestro
from rescue.models import Reporte


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
    estado_producto = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_producto",
        related_name="productos_estado",
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    existencias = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Producto"
        constraints = [
            models.CheckConstraint(condition=Q(precio__gte=0), name="ck_producto_precio"),
            models.UniqueConstraint(fields=["id_producto", "tienda"], name="uq_producto_tienda_comp"),
        ]


class ProductoImagen(models.Model):
    id_producto_imagen = models.AutoField(primary_key=True)
    archivo = models.OneToOneField(ArchivoDigital, on_delete=models.PROTECT, db_column="id_archivo")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column="id_producto")
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "ProductoImagen"
        constraints = [
            models.UniqueConstraint(fields=["producto", "orden"], name="uq_imagen_producto_orden"),
        ]


class PedidoIniciado(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, db_column="id_tienda")
    usuario_cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_cliente"
    )
    estado_pedido = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_pedido"
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "PedidoIniciado"
        constraints = [
            models.UniqueConstraint(fields=["id_pedido", "tienda"], name="uq_pedido_tienda_comp"),
        ]


class DetallePedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(PedidoIniciado, on_delete=models.PROTECT, db_column="id_pedido")
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, db_column="id_tienda")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column="id_producto")
    cantidad = models.PositiveIntegerField()
    precio_referencia = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "DetallePedido"
        constraints = [
            models.UniqueConstraint(fields=["pedido", "producto"], name="uq_detalle_pedido_producto"),
            models.CheckConstraint(condition=Q(cantidad__gt=0), name="ck_detalle_cantidad"),
            models.CheckConstraint(condition=Q(precio_referencia__gte=0), name="ck_detalle_precio"),
        ]


class EspacioPublicitario(models.Model):
    id_espacio = models.AutoField(primary_key=True)
    anunciante = models.ForeignKey(Anunciante, on_delete=models.PROTECT, db_column="id_anunciante")
    tipo_publicidad = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_tipo_publicidad",
        related_name="espacios_tipo",
    )
    estado_publicidad = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_publicidad",
        related_name="espacios_estado",
    )
    archivo = models.ForeignKey(ArchivoDigital, on_delete=models.PROTECT, db_column="id_archivo")
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    url_destino = models.URLField(max_length=2048)
    usuario_revisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_usuario_revisor",
    )
    fecha_decision = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "EspacioPublicitario"
        constraints = [
            models.CheckConstraint(condition=Q(fecha_fin__gt=F("fecha_inicio")), name="ck_pub_vigencia"),
        ]


class AlianzaVeterinaria(models.Model):
    id_alianza = models.AutoField(primary_key=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.PROTECT, db_column="id_clinica")
    nivel_alianza = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_nivel_alianza",
        related_name="alianzas_nivel",
    )
    estado_alianza = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_alianza",
        related_name="alianzas_estado",
    )
    descripcion = models.TextField(blank=True)
    tarifa = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        db_table = "AlianzaVeterinaria"
        constraints = [
            models.CheckConstraint(condition=Q(tarifa__gte=0), name="ck_alianza_tarifa"),
            models.CheckConstraint(condition=Q(fecha_fin__gte=F("fecha_inicio")), name="ck_alianza_fechas"),
        ]


class TarifaPublicacion(models.Model):
    id_tarifa = models.AutoField(primary_key=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, db_column="id_tienda")
    tipo_tarifa = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_tipo_tarifa"
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    concepto = models.CharField(max_length=200)

    class Meta:
        db_table = "TarifaPublicacion"
        constraints = [
            models.CheckConstraint(condition=Q(monto__gte=0), name="ck_tarifa_monto"),
            models.CheckConstraint(condition=Q(fecha_fin__gte=F("fecha_inicio")), name="ck_tarifa_fechas"),
        ]


class ReporteModerado(models.Model):
    id_moderacion = models.AutoField(primary_key=True)
    reporte = models.ForeignKey(Reporte, on_delete=models.PROTECT, db_column="id_reporte")
    usuario_moderador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_moderador"
    )
    resultado_moderacion = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_resultado_moderacion"
    )
    motivo = models.TextField(blank=True)
    fecha_moderacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ReporteModerado"

"""Pedido iniciado: precio referencial, sin cobro ni reserva de inventario."""

from django.db import transaction

from core.models import Notificacion, ValorMaestro
from .models import DetallePedido, PedidoIniciado, Producto


class PedidoError(ValueError):
    pass


@transaction.atomic
def iniciar_pedido(*, tienda_id, usuario_cliente_id, lineas):
    if not lineas:
        raise PedidoError("El pedido necesita al menos un producto")
    ids = [linea["id_producto"] for linea in lineas]
    if len(set(ids)) != len(ids):
        raise PedidoError("Un producto no debe repetirse en el pedido")
    productos = {
        p.pk: p for p in Producto.objects.select_for_update().select_related(
            "estado_producto__tipo", "tienda__entidad__estado_verificacion__tipo"
        ).filter(pk__in=ids)
    }
    if len(productos) != len(ids):
        raise PedidoError("Hay productos inexistentes")
    for linea in lineas:
        producto = productos[linea["id_producto"]]
        if producto.tienda_id != tienda_id:
            raise PedidoError("Todos los productos deben pertenecer a la misma tienda")
        if producto.tienda.entidad.estado_verificacion.nombre != "Verificada":
            raise PedidoError("La tienda no está verificada")
        if producto.estado_producto.tipo.nombre != "estado_producto" or producto.estado_producto.nombre != "Disponible":
            raise PedidoError("Hay productos no disponibles")
        if linea["cantidad"] <= 0 or linea["cantidad"] > producto.existencias:
            raise PedidoError("Cantidad inválida o superior a existencias")
    estado = ValorMaestro.objects.get(tipo__nombre="estado_pedido", nombre="Iniciado")
    pedido = PedidoIniciado.objects.create(
        tienda_id=tienda_id, usuario_cliente_id=usuario_cliente_id, estado_pedido=estado
    )
    for linea in lineas:
        producto = productos[linea["id_producto"]]
        DetallePedido.objects.create(
            pedido=pedido, tienda_id=tienda_id, producto=producto,
            cantidad=linea["cantidad"], precio_referencia=producto.precio,
        )
    Notificacion.objects.create(
        usuario_id=usuario_cliente_id,
        tipo_notificacion=ValorMaestro.objects.get(tipo__nombre="tipo_notificacion", nombre="Pedido iniciado"),
        contenido=f"Pedido {pedido.pk} iniciado con la tienda {pedido.tienda_id}; no se realizó ningún cobro.",
    )
    return pedido

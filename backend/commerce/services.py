"""Operaciones del catálogo; la tienda del producto es inmutable."""

from django.db import transaction

from core.models import Notificacion, ValorMaestro

from .models import DetallePedido, PedidoIniciado, Producto
from .permissions import administrador_puede, gestor_tienda_puede


class ComercioError(ValueError):
    pass


class ComercioPermisoError(ComercioError):
    pass


class ComercioNoEncontradoError(ComercioError):
    pass


def _exigir_gestor(usuario, tienda_id):
    if not (
        gestor_tienda_puede(usuario, tienda_id, "producto.gestionar")
        or administrador_puede(usuario, "producto.gestionar")
    ):
        raise ComercioPermisoError("No puede gestionar productos de esta tienda")


def _exigir_tienda_verificada(tienda):
    if tienda.entidad.estado_verificacion.tipo.nombre != "estado_verificacion" or (
        tienda.entidad.estado_verificacion.nombre != "Verificada"
    ):
        raise ComercioError("La tienda debe estar verificada")


@transaction.atomic
def crear_producto(*, usuario_actor, tienda, categoria_producto, tipo_producto, nombre,
                   precio, existencias, descripcion="", destacado=False):
    _exigir_gestor(usuario_actor, tienda.pk)
    _exigir_tienda_verificada(tienda)
    if precio <= 0 or existencias < 0:
        raise ComercioError("Precio y existencias no válidos")
    estado = ValorMaestro.objects.get(tipo__nombre="estado_producto", nombre="Disponible")
    return Producto.objects.create(
        tienda=tienda, categoria_producto=categoria_producto, tipo_producto=tipo_producto,
        nombre=nombre.strip(), descripcion=descripcion.strip(), precio=precio,
        existencias=existencias, destacado=destacado, estado_producto=estado,
    )


@transaction.atomic
def actualizar_producto(*, usuario_actor, producto_id, cambios):
    try:
        producto = Producto.objects.select_for_update().select_related(
            "tienda__entidad__estado_verificacion__tipo",
        ).get(pk=producto_id)
    except Producto.DoesNotExist as exc:
        raise ComercioNoEncontradoError("Producto inexistente") from exc
    _exigir_gestor(usuario_actor, producto.tienda_id)
    _exigir_tienda_verificada(producto.tienda)
    for campo, valor in cambios.items():
        setattr(producto, campo, valor)
    producto.save(update_fields=list(cambios))
    return producto


@transaction.atomic
def iniciar_pedido(*, usuario_cliente, tienda, productos):
    if not usuario_cliente.is_active:
        raise ComercioPermisoError("La cuenta del cliente no está activa")
    _exigir_tienda_verificada(tienda)
    if not productos or len(productos) > 50:
        raise ComercioError("El pedido requiere entre 1 y 50 productos")
    ids = [item["producto"].pk for item in productos]
    if len(ids) != len(set(ids)):
        raise ComercioError("No se puede repetir un producto en el mismo pedido")

    bloqueados = {
        producto.pk: producto
        for producto in Producto.objects.select_for_update().select_related(
            "estado_producto__tipo",
        ).filter(pk__in=ids).order_by("pk")
    }
    for item in productos:
        producto = bloqueados.get(item["producto"].pk)
        cantidad = item["cantidad"]
        if producto is None or producto.tienda_id != tienda.pk:
            raise ComercioError("Todos los productos deben pertenecer a la tienda seleccionada")
        if producto.estado_producto.tipo.nombre != "estado_producto" or (
            producto.estado_producto.nombre != "Disponible"
        ):
            raise ComercioError("Uno de los productos no está disponible")
        if cantidad <= 0 or cantidad > producto.existencias:
            raise ComercioError("Cantidad superior a las existencias disponibles")
        if producto.precio <= 0:
            raise ComercioError("Uno de los productos no tiene precio válido")

    estado = ValorMaestro.objects.get(tipo__nombre="estado_pedido", nombre="Iniciado")
    pedido = PedidoIniciado.objects.create(
        tienda=tienda, usuario_cliente=usuario_cliente, estado_pedido=estado,
    )
    for item in productos:
        producto = bloqueados[item["producto"].pk]
        DetallePedido.objects.create(
            pedido=pedido, producto=producto, cantidad=item["cantidad"],
            precio_referencia=producto.precio,
        )
    tipo_notificacion = ValorMaestro.objects.get(tipo__nombre="tipo_notificacion", nombre="Pedido iniciado")
    Notificacion.objects.create(
        usuario=usuario_cliente,
        tipo_notificacion=tipo_notificacion,
        contenido=f"Se inició el pedido {pedido.pk} para {tienda.entidad.nombre}. No implica cobro ni reserva.",
    )
    return pedido

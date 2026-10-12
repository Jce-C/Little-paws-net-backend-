"""Operaciones del catálogo; la tienda del producto es inmutable."""

from django.db import transaction

from core.models import ValorMaestro

from .models import Producto
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

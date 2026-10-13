"""Operaciones del catálogo; la tienda del producto es inmutable."""

import ipaddress
from urllib.parse import urlparse

from django.db import transaction
from django.utils import timezone

from core.models import Notificacion, Tienda, ValorMaestro

from .models import DetallePedido, EspacioPublicitario, PedidoIniciado, Producto, TarifaPublicacion
from .permissions import administrador_puede, gestor_anunciante_puede, gestor_tienda_puede


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
                   precio, existencias, descripcion="", nombre_en="", descripcion_en="", destacado=False):
    _exigir_gestor(usuario_actor, tienda.pk)
    _exigir_tienda_verificada(tienda)
    if precio <= 0 or existencias < 0:
        raise ComercioError("Precio y existencias no válidos")
    estado = ValorMaestro.objects.get(tipo__nombre="estado_producto", nombre="Disponible")
    return Producto.objects.create(
        tienda=tienda, categoria_producto=categoria_producto, tipo_producto=tipo_producto,
        nombre=nombre.strip(), nombre_en=nombre_en.strip(),
        descripcion=descripcion.strip(), descripcion_en=descripcion_en.strip(), precio=precio,
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


@transaction.atomic
def crear_espacio_publicitario(*, usuario_actor, anunciante, tipo_publicidad,
                              fecha_inicio, fecha_fin, url_destino, archivo):
    if not (
        gestor_anunciante_puede(usuario_actor, anunciante.pk, "publicidad.gestionar")
        or administrador_puede(usuario_actor, "publicidad.gestionar")
    ):
        raise ComercioPermisoError("No puede publicar anuncios para este anunciante")
    verificacion = anunciante.entidad.estado_verificacion
    if verificacion.tipo.nombre != "estado_verificacion" or verificacion.nombre != "Verificada":
        raise ComercioError("El anunciante debe estar verificado")
    if tipo_publicidad.tipo.nombre != "tipo_publicidad":
        raise ComercioError("Tipo de publicidad inválido")
    if fecha_fin <= fecha_inicio or fecha_fin <= timezone.now():
        raise ComercioError("El periodo de publicación debe ser válido y no estar vencido")
    destino = urlparse(url_destino)
    if destino.scheme != "https" or not destino.hostname or destino.username or destino.password:
        raise ComercioError("El destino debe ser una URL HTTPS pública")
    if destino.hostname.lower() == "localhost":
        raise ComercioError("El destino debe ser una URL HTTPS pública")
    try:
        direccion_ip = ipaddress.ip_address(destino.hostname)
    except ValueError:
        direccion_ip = None
    if direccion_ip is not None and not direccion_ip.is_global:
        raise ComercioError("El destino debe ser una URL HTTPS pública")
    if archivo.visibilidad != "PUBLICO" or archivo.usuario_cargador_id != usuario_actor.pk or (
        not archivo.url_archivo
    ):
        raise ComercioError("El archivo debe ser público, tener URL y pertenecer al publicador")
    return EspacioPublicitario.objects.create(
        anunciante=anunciante, tipo_publicidad=tipo_publicidad,
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
        url_destino=url_destino, archivo=archivo,
    )


@transaction.atomic
def crear_tarifa_publicacion(*, usuario_actor, tienda, tipo_tarifa, monto,
                            fecha_inicio, fecha_fin, concepto, concepto_en=""):
    if not administrador_puede(usuario_actor, "tarifa.gestionar"):
        raise ComercioPermisoError("Solo un administrador autorizado puede crear tarifas")
    tienda = Tienda.objects.select_for_update().select_related(
        "entidad__estado_verificacion__tipo",
    ).get(pk=tienda.pk)
    _exigir_tienda_verificada(tienda)
    if tipo_tarifa.tipo.nombre != "tipo_tarifa" or monto < 0 or fecha_fin < fecha_inicio:
        raise ComercioError("Tipo, monto o periodo de tarifa no válidos")
    concepto = concepto.strip()
    if not concepto:
        raise ComercioError("El concepto es obligatorio")
    if TarifaPublicacion.objects.filter(
        tienda=tienda, tipo_tarifa=tipo_tarifa,
        fecha_inicio__lte=fecha_fin, fecha_fin__gte=fecha_inicio,
    ).exists():
        raise ComercioError("Ya existe una tarifa de este tipo que se superpone en fechas")
    return TarifaPublicacion.objects.create(
        tienda=tienda, tipo_tarifa=tipo_tarifa, monto=monto,
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
        concepto=concepto, concepto_en=concepto_en.strip(),
    )

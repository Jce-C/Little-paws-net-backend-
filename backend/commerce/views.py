"""API JSON del catálogo; lectura pública y escrituras autenticadas."""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone

from core.models import EntidadMiembroRol

from .models import EspacioPublicitario, PedidoIniciado, Producto, TarifaPublicacion
from .permissions import administrador_puede, gestor_anunciante_puede
from .serializers import (
    EspacioPublicitarioCrearSerializer, PedidoCrearSerializer, TarifaPublicacionCrearSerializer,
    ProductoActualizarSerializer, ProductoCrearSerializer,
    representar_espacio, representar_pedido, representar_producto, representar_tarifa,
)
from .services import (
    ComercioError, ComercioNoEncontradoError, ComercioPermisoError,
    actualizar_producto, crear_espacio_publicitario, crear_producto,
    crear_tarifa_publicacion, iniciar_pedido,
)


def productos_publicos():
    return Producto.objects.select_related(
        "tienda__entidad", "categoria_producto", "tipo_producto", "estado_producto",
    ).filter(
        estado_producto__tipo__nombre="estado_producto", estado_producto__nombre="Disponible",
        tienda__entidad__estado_verificacion__tipo__nombre="estado_verificacion",
        tienda__entidad__estado_verificacion__nombre="Verificada",
    )


class ProductoListCreateView(APIView):
    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAuthenticated()]

    def get(self, request):
        productos = productos_publicos().order_by("-destacado", "nombre", "pk")
        return Response([representar_producto(producto) for producto in productos])

    def post(self, request):
        serializer = ProductoCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            producto = crear_producto(usuario_actor=request.user, **serializer.validated_data)
        except ComercioPermisoError as exc:
            return Response({"detalle": str(exc)}, status=403)
        except ComercioError as exc:
            return Response({"detalle": str(exc)}, status=400)
        producto = Producto.objects.select_related(
            "tienda__entidad", "categoria_producto", "tipo_producto", "estado_producto",
        ).get(pk=producto.pk)
        return Response(representar_producto(producto), status=201)


class ProductoDetalleView(APIView):
    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAuthenticated()]

    def get(self, request, producto_id):
        producto = productos_publicos().filter(pk=producto_id).first()
        if producto is None:
            return Response({"detalle": "Producto no disponible"}, status=404)
        return Response(representar_producto(producto))

    def patch(self, request, producto_id):
        serializer = ProductoActualizarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            producto = actualizar_producto(
                usuario_actor=request.user, producto_id=producto_id, cambios=serializer.validated_data,
            )
        except ComercioPermisoError as exc:
            return Response({"detalle": str(exc)}, status=403)
        except ComercioNoEncontradoError as exc:
            return Response({"detalle": str(exc)}, status=404)
        except ComercioError as exc:
            return Response({"detalle": str(exc)}, status=400)
        producto = Producto.objects.select_related(
            "tienda__entidad", "categoria_producto", "tipo_producto", "estado_producto",
        ).get(pk=producto.pk)
        return Response(representar_producto(producto))


def pedidos_visibles(usuario):
    pedidos = PedidoIniciado.objects.select_related("estado_pedido", "tienda__entidad")
    if not usuario.is_active:
        return pedidos.none()
    if administrador_puede(usuario, "pedido.consultar_tienda"):
        return pedidos
    tiendas = EntidadMiembroRol.objects.filter(
        miembro__usuario=usuario, miembro__fecha_salida__isnull=True,
        rol__codigo="GESTOR_TIENDA", rol__ambito="ENTIDAD",
        rol__rolpermiso__permiso__codigo="pedido.consultar_tienda",
    ).values("miembro__entidad_id")
    return pedidos.filter(Q(usuario_cliente=usuario) | Q(tienda_id__in=tiendas))


class PedidoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pedidos = pedidos_visibles(request.user).order_by("-fecha_inicio", "-pk")
        return Response([representar_pedido(pedido) for pedido in pedidos])

    def post(self, request):
        serializer = PedidoCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            pedido = iniciar_pedido(usuario_cliente=request.user, **serializer.validated_data)
        except ComercioPermisoError as exc:
            return Response({"detalle": str(exc)}, status=403)
        except ComercioError as exc:
            return Response({"detalle": str(exc)}, status=400)
        pedido = PedidoIniciado.objects.select_related("estado_pedido", "tienda__entidad").get(pk=pedido.pk)
        return Response(representar_pedido(pedido), status=201)


class PedidoDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pedido_id):
        pedido = pedidos_visibles(request.user).filter(pk=pedido_id).first()
        if pedido is None:
            return Response({"detalle": "Pedido inexistente o sin acceso"}, status=404)
        return Response(representar_pedido(pedido))


def espacios_base():
    return EspacioPublicitario.objects.select_related(
        "anunciante__entidad", "tipo_publicidad", "archivo",
    )


def espacios_publicos():
    ahora = timezone.now()
    return espacios_base().filter(
        fecha_inicio__lte=ahora, fecha_fin__gt=ahora,
        anunciante__entidad__estado_verificacion__tipo__nombre="estado_verificacion",
        anunciante__entidad__estado_verificacion__nombre="Verificada",
        archivo__visibilidad="PUBLICO",
    )


class EspacioPublicitarioListCreateView(APIView):
    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAuthenticated()]

    def get(self, request):
        espacios = espacios_publicos().order_by("fecha_fin", "pk")
        return Response([representar_espacio(espacio) for espacio in espacios])

    def post(self, request):
        serializer = EspacioPublicitarioCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            espacio = crear_espacio_publicitario(
                usuario_actor=request.user, **serializer.validated_data,
            )
        except ComercioPermisoError as exc:
            return Response({"detalle": str(exc)}, status=403)
        except ComercioError as exc:
            return Response({"detalle": str(exc)}, status=400)
        espacio = espacios_base().get(pk=espacio.pk)
        return Response(representar_espacio(espacio), status=201)


class EspacioPublicitarioDetalleView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, espacio_id):
        espacio = espacios_base().filter(pk=espacio_id).first()
        if espacio is None:
            return Response({"detalle": "Publicidad inexistente o sin acceso"}, status=404)
        ahora = timezone.now()
        publicado = (
            espacio.fecha_inicio <= ahora < espacio.fecha_fin
            and espacio.anunciante.entidad.estado_verificacion.tipo.nombre == "estado_verificacion"
            and espacio.anunciante.entidad.estado_verificacion.nombre == "Verificada"
            and espacio.archivo.visibilidad == "PUBLICO"
        )
        autorizado = (
            gestor_anunciante_puede(request.user, espacio.anunciante_id, "publicidad.gestionar")
            or administrador_puede(request.user, "publicidad.gestionar")
        )
        if not (publicado or autorizado):
            return Response({"detalle": "Publicidad inexistente o sin acceso"}, status=404)
        return Response(representar_espacio(espacio))


def tarifas_base():
    return TarifaPublicacion.objects.select_related("tienda__entidad", "tipo_tarifa")


def tarifas_publicas():
    hoy = timezone.localdate()
    return tarifas_base().filter(
        fecha_inicio__lte=hoy, fecha_fin__gte=hoy,
        tienda__entidad__estado_verificacion__tipo__nombre="estado_verificacion",
        tienda__entidad__estado_verificacion__nombre="Verificada",
    )


class TarifaPublicacionListCreateView(APIView):
    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAuthenticated()]

    def get(self, request):
        tarifas = tarifas_publicas().order_by("tienda_id", "tipo_tarifa_id", "pk")
        return Response([representar_tarifa(tarifa) for tarifa in tarifas])

    def post(self, request):
        serializer = TarifaPublicacionCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tarifa = crear_tarifa_publicacion(usuario_actor=request.user, **serializer.validated_data)
        except ComercioPermisoError as exc:
            return Response({"detalle": str(exc)}, status=403)
        except ComercioError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response(representar_tarifa(tarifas_base().get(pk=tarifa.pk)), status=201)


class TarifaPublicacionDetalleView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, tarifa_id):
        tarifa = tarifas_publicas().filter(pk=tarifa_id).first()
        if tarifa is None and administrador_puede(request.user, "tarifa.gestionar"):
            tarifa = tarifas_base().filter(pk=tarifa_id).first()
        if tarifa is None:
            return Response({"detalle": "Tarifa inexistente o sin acceso"}, status=404)
        return Response(representar_tarifa(tarifa))

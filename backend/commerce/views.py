"""API JSON del catálogo; lectura pública y escrituras autenticadas."""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Producto
from .serializers import ProductoActualizarSerializer, ProductoCrearSerializer, representar_producto
from .services import (
    ComercioError, ComercioNoEncontradoError, ComercioPermisoError,
    actualizar_producto, crear_producto,
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

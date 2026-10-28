from decimal import Decimal

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DetallePedido, PedidoIniciado, Producto
from .services import PedidoError, iniciar_pedido


class CatalogoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        productos = Producto.objects.select_related("tienda__entidad").filter(
            estado_producto__tipo__nombre="estado_producto",
            estado_producto__nombre="Disponible",
            tienda__entidad__estado_verificacion__nombre="Verificada",
        ).order_by("id_producto")[:100]
        return Response([
            {
                "id_producto": p.pk, "id_tienda": p.tienda_id,
                "tienda": p.tienda.entidad.nombre, "nombre": p.nombre,
                "precio": str(p.precio), "existencias": p.existencias,
            }
            for p in productos
        ])


class LineaSerializer(serializers.Serializer):
    id_producto = serializers.IntegerField(min_value=1)
    cantidad = serializers.IntegerField(min_value=1)


class PedidoCrearSerializer(serializers.Serializer):
    id_tienda = serializers.IntegerField(min_value=1)
    lineas = LineaSerializer(many=True, allow_empty=False)


class PedidoCrearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = PedidoCrearSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            pedido = iniciar_pedido(
                tienda_id=s.validated_data["id_tienda"],
                usuario_cliente_id=request.user.pk,
                lineas=s.validated_data["lineas"],
            )
        except PedidoError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_pedido": pedido.pk, "estado": "Iniciado", "cobrado": False}, status=201)


class PedidoDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pedido_id):
        pedido = PedidoIniciado.objects.filter(pk=pedido_id, usuario_cliente=request.user).first()
        if pedido is None:
            return Response({"detalle": "Pedido inexistente o sin acceso"}, status=404)
        detalles = list(DetallePedido.objects.select_related("producto").filter(pedido=pedido))
        total = sum((d.precio_referencia * d.cantidad for d in detalles), Decimal("0.00"))
        return Response({
            "id_pedido": pedido.pk, "estado": pedido.estado_pedido.nombre,
            "total_referencial": str(total), "cobrado": False,
            "lineas": [
                {
                    "id_producto": d.producto_id, "nombre": d.producto.nombre,
                    "cantidad": d.cantidad, "precio_referencia": str(d.precio_referencia),
                }
                for d in detalles
            ],
        })

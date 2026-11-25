from seguridad.participacion import Participacion
from decimal import Decimal
from django.db.models import Q

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DetallePedido, PedidoIniciado, Producto
from .services import PedidoError, iniciar_pedido
from .public_photos import disponibles, descriptor


class CatalogoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        base = disponibles()
        productos = base.select_related("tienda__entidad", "categoria_producto", "tipo_producto", "foto_publica").order_by("id_producto")
        paginated = request.query_params.get('paginado')
        if paginated is not None and paginated != '1':
            return Response({'detalle': 'Usa paginado=1.'}, status=400)
        if paginated:
            raw_limit = request.query_params.get('limite', '20')
            raw_cursor = request.query_params.get('despues', '0')
            search = request.query_params.get('buscar', '').strip()
            category = request.query_params.get('categoria', '').strip()
            if (not raw_limit.isascii() or not raw_limit.isdecimal() or not raw_cursor.isascii()
                    or not raw_cursor.isdecimal() or len(raw_cursor) > 19 or len(raw_limit) > 2
                    or not 1 <= int(raw_limit) <= 50 or int(raw_cursor) > 9223372036854775807
                    or len(search) > 100 or len(category) > 150):
                return Response({'detalle': 'Parámetros de catálogo no válidos.'}, status=400)
            if search:
                productos = productos.filter(Q(nombre__icontains=search) | Q(tienda__entidad__nombre__icontains=search))
            if category:
                productos = productos.filter(categoria_producto__nombre=category)
            rows = list(productos.filter(pk__gt=int(raw_cursor))[:int(raw_limit)+1])
            has_more = len(rows) > int(raw_limit)
            rows = rows[:int(raw_limit)]
            payload = {'results': [producto_publico(p) for p in rows],
                       'next_cursor': str(rows[-1].pk) if has_more else None}
            if raw_cursor == '0':
                payload['categorias'] = list(base.order_by('categoria_producto__nombre').values_list('categoria_producto__nombre', flat=True).distinct()[:100])
            return Response(payload)
        # Legacy clients retain the bounded list response. New clients opt in.
        return Response([producto_publico(p) for p in productos[:100]])


def producto_publico(p):
    return {
                "id_producto": p.pk, "id_tienda": p.tienda_id,
                "tienda": p.tienda.entidad.nombre, "nombre": p.nombre,
                "precio": str(p.precio), "existencias": p.existencias,
                "descripcion": p.descripcion, "categoria": p.categoria_producto.nombre,
                "tipo": p.tipo_producto.nombre,
                "foto": descriptor(p),
            }


class LineaSerializer(serializers.Serializer):
    id_producto = serializers.IntegerField(min_value=1)
    cantidad = serializers.IntegerField(min_value=1)


class PedidoCrearSerializer(serializers.Serializer):
    id_tienda = serializers.IntegerField(min_value=1)
    lineas = LineaSerializer(many=True, allow_empty=False)


class PedidoCrearView(APIView):
    permission_classes = [IsAuthenticated, Participacion]

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
        return Response(pedido_publico(pedido), status=201)


class PedidoDetalleView(APIView):
    permission_classes = [IsAuthenticated, Participacion]

    def get(self, request, pedido_id):
        pedido = PedidoIniciado.objects.filter(pk=pedido_id, usuario_cliente=request.user).first()
        if pedido is None:
            return Response({"detalle": "Pedido inexistente o sin acceso"}, status=404)
        return Response(pedido_publico(pedido))


def pedido_publico(pedido):
    detalles = list(DetallePedido.objects.select_related("producto").filter(pedido=pedido))
    total = sum((d.precio_referencia * d.cantidad for d in detalles), Decimal("0.00"))
    return {
        "id_pedido": pedido.pk, "estado": pedido.estado_pedido.nombre,
        "total_referencial": str(total), "cobrado": False,
        "lineas": [
            {
                "id_producto": d.producto_id, "nombre": d.producto.nombre,
                "cantidad": d.cantidad, "precio_referencia": str(d.precio_referencia),
            }
            for d in detalles
        ],
    }

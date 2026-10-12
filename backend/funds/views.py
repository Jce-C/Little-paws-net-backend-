"""API JSON de configuración y consulta de fondos externos."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.crypto import descifrar

from .models import FondoExterno
from .serializers import FondoExternoCrearSerializer, representar_fondo
from .services import FondoError, FondoPermisoError, crear_fondo_externo


class FondoExternoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fondos = FondoExterno.objects.order_by("nombre", "pk")
        return Response([representar_fondo(fondo) for fondo in fondos])

    def post(self, request):
        serializer = FondoExternoCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            fondo = crear_fondo_externo(
                usuario_actor=request.user,
                **serializer.validated_data,
            )
        except FondoPermisoError as exc:
            return Response({"detalle": str(exc)}, status=403)
        except FondoError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response(representar_fondo(fondo), status=201)


class FondoExternoInstruccionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, fondo_id):
        fondo = FondoExterno.objects.filter(pk=fondo_id).first()
        if fondo is None:
            return Response({"detalle": "Fondo inexistente"}, status=404)
        return Response({
            "id_fondo_externo": fondo.pk,
            "instrucciones_transferencia": descifrar(fondo.datos_transferencia_cifrados),
            "aviso": "Transferencia externa; Little Paws Net no procesa el pago",
        })

"""API JSON de configuración y consulta de fondos externos."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.crypto import descifrar

from .models import DonacionGeneral, FondoExterno
from .permissions import administrador_puede
from .serializers import (
    CompromisoDonacionCrearSerializer, FondoExternoCrearSerializer,
    ResolverDonacionSerializer, representar_donacion, representar_fondo,
)
from .services import (
    FondoError, FondoNoEncontradoError, FondoPermisoError, FondoTransicionError,
    crear_compromiso_donacion, crear_fondo_externo, resolver_compromiso_donacion,
)


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


def donaciones_visibles(usuario):
    donaciones = DonacionGeneral.objects.select_related("fondo_externo", "estado_donacion")
    if administrador_puede(usuario, "donacion.confirmar"):
        return donaciones
    return donaciones.filter(usuario_donante=usuario)


class DonacionGeneralListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        donaciones = donaciones_visibles(request.user).order_by("-fecha_compromiso", "-pk")
        return Response([representar_donacion(donacion) for donacion in donaciones])

    def post(self, request):
        serializer = CompromisoDonacionCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            donacion = crear_compromiso_donacion(
                usuario_donante=request.user,
                **serializer.validated_data,
            )
        except FondoPermisoError as exc:
            return Response({"detalle": str(exc)}, status=403)
        except FondoError as exc:
            return Response({"detalle": str(exc)}, status=400)
        donacion = DonacionGeneral.objects.select_related("fondo_externo", "estado_donacion").get(pk=donacion.pk)
        return Response(representar_donacion(donacion), status=201)


class DonacionGeneralDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, donacion_id):
        donacion = donaciones_visibles(request.user).filter(pk=donacion_id).first()
        if donacion is None:
            return Response({"detalle": "Donación inexistente o sin acceso"}, status=404)
        return Response(representar_donacion(donacion, incluir_historial=True))


class ResolverDonacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, donacion_id):
        serializer = ResolverDonacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            donacion = resolver_compromiso_donacion(
                donacion_id=donacion_id,
                usuario_actor=request.user,
                **serializer.validated_data,
            )
        except FondoPermisoError as exc:
            return Response({"detalle": str(exc)}, status=403)
        except FondoNoEncontradoError as exc:
            return Response({"detalle": str(exc)}, status=404)
        except FondoTransicionError as exc:
            return Response({"detalle": str(exc)}, status=409)
        except FondoError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({
            "id_donacion": donacion.pk,
            "estado": donacion.estado_donacion.nombre,
            "aviso": representar_donacion(donacion)["aviso"],
        })

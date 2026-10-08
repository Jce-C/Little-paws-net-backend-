"""APIs JSON de apadrinamientos y aportes externos."""

from django.core.exceptions import ImproperlyConfigured
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.crypto import cifrar

from .models import Apadrinamiento, CuentaFundacion, DeclaracionTransferencia
from .serializers import (
    CompromisoSerializer, ConfirmacionSerializer, CuentaCrearSerializer, DeclaracionSerializer,
)
from .services import miembro_puede
from .sponsorship import (
    ApadrinamientoError, confirmar_aporte, crear_compromiso, revelar_cuenta,
)


class CompromisoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompromisoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            apadrinamiento = crear_compromiso(
                reporte_id=serializer.validated_data["id_reporte"],
                usuario_padrino_id=request.user.pk,
                monto=serializer.validated_data["monto_comprometido"],
            )
        except ApadrinamientoError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_apadrinamiento": apadrinamiento.pk, "estado": "En espera"}, status=201)


class CuentaCrearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, fundacion_id):
        if not miembro_puede(fundacion_id, request.user.pk, "aporte.confirmar"):
            return Response({"detalle": "Sin permiso para esta fundación"}, status=403)
        serializer = CuentaCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        try:
            cifrado = cifrar(datos["numero_cuenta"])
        except ImproperlyConfigured:
            return Response({"detalle": "Cifrado no configurado"}, status=503)
        cuenta = CuentaFundacion.objects.create(
            fundacion_id=fundacion_id, numero_cuenta_cifrado=cifrado,
            numero_cuenta_ultimos4=datos["numero_cuenta"][-4:],
            banco=datos["banco"], tipo_cuenta=datos["tipo_cuenta"], titular=datos["titular"],
        )
        return Response({"id_cuenta": cuenta.pk, "ultimos4": cuenta.numero_cuenta_ultimos4}, status=201)


class CuentaRevelarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, apadrinamiento_id):
        try:
            cuenta, numero = revelar_cuenta(
                apadrinamiento_id=apadrinamiento_id, usuario_padrino_id=request.user.pk,
            )
        except ApadrinamientoError as exc:
            return Response({"detalle": str(exc)}, status=400)
        except (ImproperlyConfigured, ValueError):
            return Response({"detalle": "Datos bancarios no disponibles"}, status=503)
        respuesta = Response({
            "banco": cuenta.banco, "tipo_cuenta": cuenta.tipo_cuenta,
            "titular": cuenta.titular, "numero_cuenta": numero,
            "nota": "La transferencia se realiza fuera de Little Paws Net.",
        })
        respuesta["Cache-Control"] = "no-store"
        return respuesta


class DeclaracionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, apadrinamiento_id):
        serializer = DeclaracionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        apadrinamiento = Apadrinamiento.objects.filter(
            pk=apadrinamiento_id, usuario_padrino=request.user,
        ).first()
        if apadrinamiento is None:
            return Response({"detalle": "Apadrinamiento inexistente o sin acceso"}, status=404)
        try:
            referencia = (
                cifrar(serializer.validated_data["referencia"])
                if serializer.validated_data.get("referencia") else None
            )
        except ImproperlyConfigured:
            return Response({"detalle": "Cifrado no configurado"}, status=503)
        declaracion = DeclaracionTransferencia.objects.create(
            apadrinamiento=apadrinamiento,
            monto_declarado=serializer.validated_data["monto_declarado"],
            referencia_cifrada=referencia,
            fecha_transferencia_declarada=serializer.validated_data["fecha_transferencia_declarada"],
        )
        return Response({"id_declaracion": declaracion.pk, "recibido": False}, status=201)


class ConfirmacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, apadrinamiento_id):
        serializer = ConfirmacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            confirmacion = confirmar_aporte(
                apadrinamiento_id=apadrinamiento_id,
                usuario_confirmador_id=request.user.pk,
                monto=serializer.validated_data["monto_confirmado"],
            )
        except ApadrinamientoError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_confirmacion": confirmacion.pk, "estado": "Aceptado"}, status=201)

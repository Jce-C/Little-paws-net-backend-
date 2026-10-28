"""Registro informativo del fondo externo; nunca procesa transferencias."""

from decimal import Decimal

from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import EntidadMiembroRol, Fundacion, Rol, ValorMaestro
from rescue.sponsorship import miembro_puede
from .models import DistribucionReportadaFondo, DonacionGeneral, FondoExterno, SolicitudEmergencia
from seguridad.autorizacion import puede


def puede_fondo(fondo, usuario_id):
    if fondo.entidad_id is None:
        return False
    return puede(usuario_id, "fondo.reportar_distribucion", entidad_id=fondo.entidad_id, objeto_id=fondo.pk)


class FondosView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        fondos = FondoExterno.objects.filter(estado_fondo__nombre="Activo").order_by("id_fondo_externo")[:100]
        return Response([
            {"id_fondo_externo": f.pk, "nombre": f.nombre, "administradora": f.entidad_administradora}
            for f in fondos
        ])


class DonacionSerializer(serializers.Serializer):
    id_fondo_externo = serializers.IntegerField(min_value=1)
    monto_comprometido = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))


class DonacionCrearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = DonacionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        fondo = FondoExterno.objects.filter(
            pk=s.validated_data["id_fondo_externo"], estado_fondo__nombre="Activo"
        ).first()
        if fondo is None:
            return Response({"detalle": "Fondo no disponible"}, status=400)
        donacion = DonacionGeneral.objects.create(
            fondo_externo=fondo,
            usuario_donante=request.user,
            estado_donacion=ValorMaestro.objects.get(tipo__nombre="estado_donacion", nombre="Comprometida"),
            monto_comprometido=s.validated_data["monto_comprometido"],
        )
        return Response({"id_donacion": donacion.pk, "dinero_recibido": False}, status=201)


class EmergenciaSerializer(serializers.Serializer):
    id_fondo_externo = serializers.IntegerField(min_value=1)
    motivo = serializers.CharField(max_length=5000)
    monto_solicitado = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))


class EmergenciaCrearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, fundacion_id):
        if not miembro_puede(fundacion_id, request.user.pk, "fondo.solicitar"):
            return Response({"detalle": "Sin permiso para esta fundación"}, status=403)
        s = EmergenciaSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        fondo = FondoExterno.objects.filter(
            pk=s.validated_data["id_fondo_externo"], estado_fondo__nombre="Activo"
        ).first()
        if fondo is None:
            return Response({"detalle": "Fondo no disponible"}, status=400)
        solicitud = SolicitudEmergencia.objects.create(
            fundacion_id=fundacion_id,
            fondo_externo=fondo,
            estado_emergencia=ValorMaestro.objects.get(tipo__nombre="estado_emergencia", nombre="Pendiente"),
            motivo=s.validated_data["motivo"],
            monto_solicitado=s.validated_data["monto_solicitado"],
        )
        return Response({"id_solicitud_emergencia": solicitud.pk}, status=201)


class DistribucionSerializer(serializers.Serializer):
    id_fundacion = serializers.IntegerField(min_value=1)
    monto_reportado = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    fecha_distribucion = serializers.DateTimeField()
    criterio = serializers.CharField(max_length=5000)


class DistribucionCrearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, fondo_id):
        s = DistribucionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        fondo = FondoExterno.objects.filter(pk=fondo_id, estado_fondo__nombre="Activo").first()
        if fondo is None:
            return Response({"detalle": "Fondo no disponible"}, status=400)
        if not puede_fondo(fondo, request.user.pk):
            return Response({"detalle": "Sin permiso para reportar por este fondo"}, status=403)
        if not Fundacion.objects.filter(pk=s.validated_data["id_fundacion"]).exists():
            return Response({"detalle": "Fundación inexistente"}, status=400)
        distribucion = DistribucionReportadaFondo.objects.create(
            fondo_externo=fondo,
            fundacion_id=s.validated_data["id_fundacion"],
            estado_distribucion=ValorMaestro.objects.get(
                tipo__nombre="estado_distribucion", nombre="Reportada"
            ),
            monto_reportado=s.validated_data["monto_reportado"],
            fecha_distribucion=s.validated_data["fecha_distribucion"],
            criterio=s.validated_data["criterio"],
        )
        return Response({"id_distribucion": distribucion.pk, "transferencia_verificada": False}, status=201)

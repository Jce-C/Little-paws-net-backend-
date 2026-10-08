"""API del expediente: QR no sustituye verificación ni autorización."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HistorialMedico
from .serializers import (
    AccesoQRSerializer, AtencionExternaSerializer, AtencionSerializer,
    AutorizarVeterinarioSerializer, RegenerarQRSerializer,
)
from .services import (
    ExpedienteError, autorizar_veterinario, regenerar_qr, registrar_atencion,
    registrar_atencion_externa, registrar_custodia, veterinario_con_acceso,
)


class CustodiaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, caso_id):
        try:
            custodia = registrar_custodia(caso_id=caso_id, usuario_id=request.user.pk)
        except ExpedienteError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_custodia": custodia.pk, "id_mascota": custodia.mascota_id}, status=201)


class AutorizacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, mascota_id):
        serializer = AutorizarVeterinarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            autorizacion = autorizar_veterinario(
                mascota_id=mascota_id, usuario_id=request.user.pk,
                veterinario_id=serializer.validated_data["id_veterinario"],
                dias=serializer.validated_data["dias"],
            )
        except ExpedienteError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_autorizacion": autorizacion.pk, "expira": autorizacion.fecha_expiracion}, status=201)


class QRView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, mascota_id):
        serializer = RegenerarQRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            qr, token = regenerar_qr(
                mascota_id=mascota_id, usuario_id=request.user.pk,
                horas=serializer.validated_data["horas"],
            )
        except ExpedienteError as exc:
            return Response({"detalle": str(exc)}, status=400)
        respuesta = Response({"id_qr": qr.pk, "codigo_qr": token, "expira": qr.fecha_expiracion}, status=201)
        respuesta["Cache-Control"] = "no-store"
        return respuesta


class ExpedienteConsultarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, mascota_id):
        serializer = AccesoQRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            veterinario_con_acceso(
                mascota_id=mascota_id, usuario_id=request.user.pk,
                token=serializer.validated_data["codigo_qr"],
            )
        except ExpedienteError as exc:
            return Response({"detalle": str(exc)}, status=403)
        registros = HistorialMedico.objects.filter(mascota_id=mascota_id).order_by("fecha_atencion", "pk")
        respuesta = Response({
            "id_mascota": mascota_id,
            "registros": [{
                "id_historial_medico": registro.pk,
                "fecha_atencion": registro.fecha_atencion,
                "detalle": registro.detalle,
                "id_veterinario": registro.veterinario_id,
                "nombre_veterinario_externo": registro.nombre_veterinario_externo,
            } for registro in registros],
        })
        respuesta["Cache-Control"] = "no-store"
        return respuesta


class AtencionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, mascota_id):
        serializer = AtencionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            registro = registrar_atencion(
                mascota_id=mascota_id, usuario_id=request.user.pk,
                token=serializer.validated_data["codigo_qr"],
                detalle=serializer.validated_data["detalle"],
                fecha_atencion=serializer.validated_data["fecha_atencion"],
            )
        except ExpedienteError as exc:
            return Response({"detalle": str(exc)}, status=403)
        return Response({"id_historial_medico": registro.pk}, status=201)


class AtencionExternaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, mascota_id):
        serializer = AtencionExternaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            registro = registrar_atencion_externa(
                mascota_id=mascota_id, usuario_id=request.user.pk,
                nombre=serializer.validated_data["nombre_veterinario_externo"],
                matricula=serializer.validated_data["registro_profesional_externo"],
                detalle=serializer.validated_data["detalle"],
                fecha_atencion=serializer.validated_data["fecha_atencion"],
            )
        except ExpedienteError as exc:
            return Response({"detalle": str(exc)}, status=403)
        return Response({"id_historial_medico": registro.pk, "verificado_por": request.user.pk}, status=201)

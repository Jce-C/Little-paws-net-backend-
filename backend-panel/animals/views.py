"""Vistas JSON para autorización, QR y anotación médica."""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AtencionSerializer, AutorizarSerializer
from .services import (
    ExpedienteError, autorizar_veterinario, mascota_desde_qr, regenerar_qr, registrar_atencion,
)


class AutorizarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, mascota_id):
        s = AutorizarSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            autorizacion = autorizar_veterinario(
                mascota_id=mascota_id,
                veterinario_id=s.validated_data["id_veterinario"],
                usuario_otorgante_id=request.user.pk,
                horas=s.validated_data["horas"],
            )
        except ExpedienteError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_autorizacion": autorizacion.pk, "expira": autorizacion.fecha_expiracion}, status=201)


class QRCrearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, mascota_id):
        try:
            qr, token = regenerar_qr(mascota_id=mascota_id, usuario_creador_id=request.user.pk)
        except ExpedienteError as exc:
            return Response({"detalle": str(exc)}, status=400)
        respuesta = Response({"id_qr": qr.pk, "codigo": token, "expira": qr.fecha_expiracion}, status=201)
        respuesta["Cache-Control"] = "no-store"
        return respuesta


class QRConsultarView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            mascota = mascota_desde_qr(token)
        except ExpedienteError as exc:
            return Response({"detalle": str(exc)}, status=404)
        # Ningún dato médico o de contacto se expone sin autenticación/autorización.
        return Response({"id_mascota": mascota.pk, "nombre": mascota.nombre})


class AtencionCrearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, token):
        s = AtencionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            registro = registrar_atencion(
                token_qr=token, usuario_veterinario_id=request.user.pk,
                detalle=s.validated_data["detalle"],
                fecha_atencion=s.validated_data["fecha_atencion"],
            )
        except ExpedienteError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_historial_medico": registro.pk}, status=201)

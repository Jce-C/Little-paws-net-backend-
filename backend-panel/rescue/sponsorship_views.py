from seguridad.participacion import Participacion
"""Vistas JSON de compromisos, cuentas, declaraciones y confirmaciones."""

from django.core.exceptions import ImproperlyConfigured
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.crypto import cifrar
from .models import Apadrinamiento, DeclaracionTransferencia
from .serializers import (
    CompromisoSerializer, ConfirmacionSerializer, DeclaracionSerializer,
)
from .sponsorship import (
    ApadrinamientoError, confirmar_aporte, crear_compromiso, revelar_cuenta,
)


class CompromisoView(APIView):
    permission_classes = [IsAuthenticated, Participacion]

    def post(self, request):
        s = CompromisoSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        from core.operation_receipts import crear_una_vez
        return crear_una_vez(request, 'apadrinamiento', s.validated_data, lambda:self._create(request, s.validated_data))

    def _create(self, request, data):
        try:
            apad = crear_compromiso(
                reporte_id=data["id_reporte"],
                usuario_padrino_id=request.user.pk,
                monto=data["monto_comprometido"],
            )
        except ApadrinamientoError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_apadrinamiento": apad.pk, "estado": "En espera"}, status=201)


class CuentaCrearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, fundacion_id):
        # Se retira la vía histórica que usaba aporte.confirmar para publicar cuentas.
        # El circuito vigente está en seguridad/operaciones; esta ruta no lo omite.
        return Response({"detalle": "La publicación directa de cuentas está deshabilitada; requiere el circuito de propuesta y aprobación"}, status=409)


class CuentaRevelarView(APIView):
    permission_classes = [IsAuthenticated, Participacion]

    def get(self, request, apadrinamiento_id):
        try:
            cuenta, numero = revelar_cuenta(
                apadrinamiento_id=apadrinamiento_id,
                usuario_padrino_id=request.user.pk,
            )
        except ApadrinamientoError as exc:
            return Response({"detalle": str(exc)}, status=400)
        except (ImproperlyConfigured, ValueError):
            return Response({"detalle": "Datos bancarios no disponibles"}, status=503)
        respuesta = Response({
            "organizacion": cuenta.fundacion.entidad.nombre, "organizacion_id": cuenta.fundacion_id,
            "banco": cuenta.banco, "tipo_cuenta": cuenta.tipo_cuenta,
            "titular": cuenta.titular, "numero_cuenta": numero,
            "nota": "La transferencia se realiza fuera de Little Paws Net.",
        })
        respuesta["Cache-Control"] = "no-store"
        return respuesta


class DeclaracionView(APIView):
    permission_classes = [IsAuthenticated, Participacion]

    def post(self, request, apadrinamiento_id):
        s = DeclaracionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        apad = Apadrinamiento.objects.filter(pk=apadrinamiento_id, usuario_padrino=request.user).first()
        if apad is None:
            return Response({"detalle": "Apadrinamiento inexistente o sin acceso"}, status=404)
        try:
            referencia = (
                cifrar(s.validated_data["referencia"])
                if s.validated_data.get("referencia") else None
            )
        except ImproperlyConfigured:
            return Response({"detalle": "Cifrado no configurado"}, status=503)
        declaracion = DeclaracionTransferencia.objects.create(
            apadrinamiento=apad,
            monto_declarado=s.validated_data["monto_declarado"],
            referencia_cifrada=referencia,
            fecha_transferencia_declarada=s.validated_data["fecha_transferencia_declarada"],
        )
        return Response({"id_declaracion": declaracion.pk, "recibido": False}, status=status.HTTP_201_CREATED)


class ConfirmacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, apadrinamiento_id):
        s = ConfirmacionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            conf = confirmar_aporte(
                apadrinamiento_id=apadrinamiento_id,
                usuario_confirmador_id=request.user.pk,
                monto=s.validated_data["monto_confirmado"],
            )
        except ApadrinamientoError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_confirmacion": conf.pk, "estado": "Aceptado"}, status=201)


class MisCompromisosView(APIView):
    permission_classes = [IsAuthenticated, Participacion]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        return response

    def get(self, request):
        from rest_framework import serializers
        before = request.query_params.get('antes')
        before = serializers.IntegerField(min_value=1, max_value=2147483647).run_validation(before) if before is not None else None
        rows = Apadrinamiento.objects.filter(usuario_padrino=request.user).select_related('estado_apadrinamiento','reporte__casorescate__fundacion__entidad').order_by('-pk')
        if before is not None:
            rows = rows.filter(pk__lt=before)
        page = list(rows[:21]);more = len(page)>20;page = page[:20]
        result = []
        for row in page:
            case = getattr(row.reporte, 'casorescate', None)
            result.append({'id_apadrinamiento':row.pk, 'reporte_id':row.reporte_id, 'monto_comprometido':str(row.monto_comprometido), 'fecha_compromiso':row.fecha_compromiso, 'estado':row.estado_apadrinamiento.nombre, 'organizacion':case.fundacion.entidad.nombre if case else 'Sin organización asignada'})
        return Response({'results':result,'next_cursor':str(page[-1].pk) if more else None})

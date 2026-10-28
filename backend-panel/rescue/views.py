"""Vistas JSON del reporte y rescate."""

import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from rest_framework.views import APIView

from core.models import ValorMaestro
from geography.models import ReporteUbicacion
from .models import CasoRescate, HistorialEstadoReporte, Reporte
from .serializers import AceptarSerializer, GestionAnonimaSerializer, ReporteCrearSerializer
from .services import ReglaNegocioError, aceptar_reporte
from seguridad.autorizacion import puede


class ReporteCrearView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @transaction.atomic
    def post(self, request):
        serializer = ReporteCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        anonimo = not request.user.is_authenticated
        codigo = secrets.token_urlsafe(24) if anonimo else None
        estado = ValorMaestro.objects.get(tipo__nombre="estado_reporte", nombre="Pendiente")
        reporte = Reporte.objects.create(
            usuario_reportante=None if anonimo else request.user,
            codigo_gestion_hash=make_password(codigo) if anonimo else "",
            estado_reporte=estado,
            tipo_reporte=data["tipo_reporte"],
            mascota=data.get("mascota"),
            descripcion=data["descripcion"],
            contacto_reportante=data.get("contacto_reportante", ""),
        )
        ReporteUbicacion.objects.create(
            reporte=reporte,
            latitud=data["latitud"], longitud=data["longitud"],
        )
        resultado = {"id_reporte": reporte.pk, "estado": "Pendiente"}
        if codigo is not None:
            resultado["codigo_gestion"] = codigo  # Solo esta respuesta; se almacena el hash.
        return Response(resultado, status=status.HTTP_201_CREATED)


class GestionAnonimaView(APIView):
    """La clave de un reporte anónimo permite editarlo solo antes de su aceptación."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "anon_report"

    @transaction.atomic
    def post(self, request, reporte_id):
        serializer = GestionAnonimaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        reporte = Reporte.objects.select_for_update().filter(pk=reporte_id).first()
        if reporte is None or reporte.usuario_reportante_id is not None:
            return Response({"detalle": "Reporte no disponible"}, status=status.HTTP_404_NOT_FOUND)
        if not check_password(data["codigo_gestion"], reporte.codigo_gestion_hash):
            return Response({"detalle": "Credencial inválida"}, status=status.HTTP_403_FORBIDDEN)
        if reporte.estado_reporte.nombre != "Pendiente" or CasoRescate.objects.filter(reporte=reporte).exists():
            return Response({"detalle": "El reporte ya no admite cambios"}, status=status.HTTP_409_CONFLICT)
        campos = ["fecha_actualizacion"]
        for campo in ("descripcion", "contacto_reportante"):
            if campo in data:
                setattr(reporte, campo, data[campo])
                campos.append(campo)
        if data["cerrar"]:
            anterior = reporte.estado_reporte
            reporte.estado_reporte = ValorMaestro.objects.get(tipo__nombre="estado_reporte", nombre="Cerrado")
            campos.append("estado_reporte")
            HistorialEstadoReporte.objects.create(
                reporte=reporte, estado_anterior=anterior, estado_nuevo=reporte.estado_reporte,
                usuario_actor=None, observacion="Cierre solicitado con clave privada por reportante anónimo",
            )
        reporte.save(update_fields=campos)
        return Response({"id_reporte": reporte.pk, "estado": reporte.estado_reporte.nombre})


class AceptarReporteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reporte_id):
        serializer = AceptarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            caso = aceptar_reporte(
                reporte_id=reporte_id,
                fundacion_id=serializer.validated_data["id_fundacion"],
                usuario_actor_id=request.user.pk,
                justificacion_sin_cupo=serializer.validated_data.get("justificacion_sin_cupo", ""),
            )
        except ReglaNegocioError as exc:
            return Response({"detalle": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"id_caso": caso.pk, "id_reporte": caso.reporte_id}, status=status.HTTP_201_CREATED)


class CasoDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, caso_id):
        caso = CasoRescate.objects.select_related("reporte", "fundacion__entidad", "estado_caso").filter(
            pk=caso_id
        ).first()
        if caso is None:
            return Response({"detalle": "Caso inexistente"}, status=status.HTTP_404_NOT_FOUND)
        es_reportante = caso.reporte.usuario_reportante_id == request.user.pk
        es_gestor = puede(request.user, "caso.ver", entidad_id=caso.fundacion_id)
        if not (es_reportante or es_gestor):
            return Response({"detalle": "Sin acceso al caso"}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "id_caso": caso.pk,
            "id_reporte": caso.reporte_id,
            "fundacion": caso.fundacion.entidad.nombre,
            "estado": caso.estado_caso.nombre,
            "fecha_aceptacion": caso.fecha_aceptacion,
        })

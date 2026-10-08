"""Endpoints JSON de reporte, rescate y seguimiento."""

import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from core.models import ValorMaestro

from .models import CasoRescate, HistorialEstadoReporte, Reporte, ReporteUbicacion
from .serializers import (
    AceptarReporteSerializer, CerrarCasoSerializer, GestionAnonimaSerializer, ReporteCrearSerializer,
)
from .services import ReglaNegocioError, aceptar_reporte, cerrar_caso


class ReporteCrearView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @transaction.atomic
    def post(self, request):
        serializer = ReporteCrearSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        anonimo = not request.user.is_authenticated
        codigo = secrets.token_urlsafe(24) if anonimo else None
        estado = ValorMaestro.objects.get(tipo__nombre="estado_reporte", nombre="Pendiente")
        reporte = Reporte.objects.create(
            usuario_reportante=None if anonimo else request.user,
            codigo_gestion_hash=make_password(codigo) if anonimo else "",
            estado_reporte=estado, tipo_reporte=datos["tipo_reporte"],
            mascota=datos.get("mascota"), descripcion=datos["descripcion"],
            contacto_reportante=datos.get("contacto_reportante", ""),
        )
        ReporteUbicacion.objects.create(
            reporte=reporte, latitud=datos["latitud"], longitud=datos["longitud"],
        )
        HistorialEstadoReporte.objects.create(
            reporte=reporte, estado_nuevo=estado, usuario_actor=None if anonimo else request.user,
            observacion="Creación del reporte",
        )
        respuesta = {"id_reporte": reporte.pk, "estado": "Pendiente"}
        if codigo:
            respuesta["codigo_gestion"] = codigo
        return Response(respuesta, status=status.HTTP_201_CREATED)


class GestionAnonimaView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @transaction.atomic
    def post(self, request, reporte_id):
        serializer = GestionAnonimaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        reporte = Reporte.objects.select_for_update().filter(pk=reporte_id, usuario_reportante__isnull=True).first()
        if reporte is None:
            return Response({"detalle": "Reporte no disponible"}, status=404)
        if not check_password(datos["codigo_gestion"], reporte.codigo_gestion_hash):
            return Response({"detalle": "Credencial inválida"}, status=403)
        if reporte.estado_reporte.nombre != "Pendiente" or CasoRescate.objects.filter(reporte=reporte).exists():
            return Response({"detalle": "El reporte ya no admite cambios"}, status=409)
        campos = ["fecha_actualizacion"]
        for campo in ("descripcion", "contacto_reportante"):
            if campo in datos:
                setattr(reporte, campo, datos[campo])
                campos.append(campo)
        if datos["cerrar"]:
            anterior = reporte.estado_reporte
            reporte.estado_reporte = ValorMaestro.objects.get(tipo__nombre="estado_reporte", nombre="Cerrado")
            campos.append("estado_reporte")
            HistorialEstadoReporte.objects.create(
                reporte=reporte, estado_anterior=anterior, estado_nuevo=reporte.estado_reporte,
                observacion="Cierre solicitado con código privado",
            )
        reporte.save(update_fields=campos)
        return Response({"id_reporte": reporte.pk, "estado": reporte.estado_reporte.nombre})


class ReporteDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reporte_id):
        reporte = Reporte.objects.select_related("estado_reporte", "tipo_reporte").filter(pk=reporte_id).first()
        if reporte is None:
            return Response({"detalle": "Reporte inexistente"}, status=404)
        caso = CasoRescate.objects.select_related("estado_caso", "fundacion__entidad").filter(reporte=reporte).first()
        es_reportante = reporte.usuario_reportante_id == request.user.pk
        es_miembro = bool(caso and caso.fundacion.entidad.entidadmiembro_set.filter(
            usuario=request.user, fecha_salida__isnull=True,
        ).exists())
        if not (es_reportante or es_miembro):
            return Response({"detalle": "Sin acceso al reporte"}, status=403)
        return Response({
            "id_reporte": reporte.pk, "tipo": reporte.tipo_reporte.nombre,
            "estado": reporte.estado_reporte.nombre, "fecha_creacion": reporte.fecha_creacion,
            "caso": None if caso is None else {
                "id_caso": caso.pk, "fundacion": caso.fundacion.entidad.nombre,
                "estado": caso.estado_caso.nombre,
            },
        })


class AceptarReporteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reporte_id):
        serializer = AceptarReporteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            caso = aceptar_reporte(
                reporte_id=reporte_id,
                fundacion_id=serializer.validated_data["id_fundacion"],
                usuario_actor_id=request.user.pk,
                justificacion_sin_cupo=serializer.validated_data.get("justificacion_sin_cupo", ""),
            )
        except ReglaNegocioError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_caso": caso.pk, "id_reporte": caso.reporte_id}, status=201)


class CasoDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, caso_id):
        caso = CasoRescate.objects.select_related("reporte", "fundacion__entidad", "estado_caso").filter(pk=caso_id).first()
        if caso is None:
            return Response({"detalle": "Caso inexistente"}, status=404)
        es_reportante = caso.reporte.usuario_reportante_id == request.user.pk
        es_miembro = caso.fundacion.entidad.entidadmiembro_set.filter(
            usuario=request.user, fecha_salida__isnull=True,
        ).exists()
        if not (es_reportante or es_miembro):
            return Response({"detalle": "Sin acceso al caso"}, status=403)
        return Response({
            "id_caso": caso.pk, "id_reporte": caso.reporte_id,
            "fundacion": caso.fundacion.entidad.nombre, "estado": caso.estado_caso.nombre,
            "fecha_aceptacion": caso.fecha_aceptacion,
        })


class CerrarCasoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, caso_id):
        serializer = CerrarCasoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            caso = cerrar_caso(
                caso_id=caso_id, usuario_actor_id=request.user.pk,
                nuevo_estado=serializer.validated_data["estado"],
                observacion=serializer.validated_data.get("observacion", ""),
            )
        except ReglaNegocioError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_caso": caso.pk, "estado": caso.estado_caso.nombre})

"""Endpoints JSON para solicitudes de adopcion."""

from django.db.models import Exists, OuterRef, Q
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from animals.models import CustodiaMascota
from core.i18n import error, etiqueta, texto

from .models import SolicitudAdopcion
from .serializers import (
    ResolverSolicitudAdopcionSerializer, SolicitudAdopcionCrearSerializer, representar_solicitud,
)
from .services import (
    AdopcionError, AdopcionPermisoError, _admin_puede_resolver,
    crear_solicitud_adopcion, resolver_solicitud_adopcion,
)


def solicitudes_visibles(usuario):
    solicitudes = SolicitudAdopcion.objects.select_related(
            "mascota",
            "estado_adopcion",
    )
    if _admin_puede_resolver(usuario.pk):
        return solicitudes
    custodia_al_solicitar = CustodiaMascota.objects.filter(
        mascota_id=OuterRef("mascota_id"),
        fecha_inicio__lte=OuterRef("fecha_solicitud"),
        fundacion__entidad__entidadmiembro__usuario=usuario,
        fundacion__entidad__entidadmiembro__fecha_salida__isnull=True,
        fundacion__entidad__entidadmiembro__entidadmiembrorol__rol__codigo="GESTOR_FUNDACION",
        fundacion__entidad__entidadmiembro__entidadmiembrorol__rol__ambito="ENTIDAD",
        fundacion__entidad__entidadmiembro__entidadmiembrorol__rol__rolpermiso__permiso__codigo="adopcion.resolver",
    ).filter(Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=OuterRef("fecha_solicitud")))
    return (
        solicitudes.annotate(gestor_custodio=Exists(custodia_al_solicitar))
        .filter(Q(usuario_adoptante=usuario) | Q(gestor_custodio=True))
    )


class SolicitudAdopcionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        solicitudes = solicitudes_visibles(request.user).order_by("-fecha_solicitud", "-pk")
        mascota_id = request.query_params.get("id_mascota")
        if mascota_id:
            try:
                mascota_id = serializers.IntegerField(min_value=1).run_validation(mascota_id)
            except serializers.ValidationError:
                return Response({"id_mascota": [texto("Debe ser un entero positivo.", "Must be a positive integer.")]}, status=400)
            solicitudes = solicitudes.filter(mascota_id=mascota_id)
        return Response([representar_solicitud(solicitud) for solicitud in solicitudes])

    def post(self, request):
        serializer = SolicitudAdopcionCrearSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        try:
            solicitud = crear_solicitud_adopcion(
                mascota_id=datos["id_mascota"],
                usuario_id=request.user.pk,
                observaciones=datos.get("observaciones", ""),
            )
        except AdopcionError as exc:
            return Response({"detalle": error(str(exc))}, status=400)
        solicitud = SolicitudAdopcion.objects.select_related(
            "mascota",
            "estado_adopcion",
        ).get(pk=solicitud.pk)
        return Response(representar_solicitud(solicitud), status=201)


class SolicitudAdopcionDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, solicitud_id):
        solicitud = solicitudes_visibles(request.user).filter(pk=solicitud_id).first()
        if solicitud is None:
            return Response({"detalle": texto("Solicitud inexistente o sin acceso", "Application not found or access denied")}, status=404)
        return Response(representar_solicitud(solicitud, incluir_historial=True))


class ResolverSolicitudAdopcionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, solicitud_id):
        serializer = ResolverSolicitudAdopcionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            solicitud = resolver_solicitud_adopcion(
                solicitud_id=solicitud_id,
                usuario_actor_id=request.user.pk,
                estado=serializer.validated_data["estado"],
                observacion=serializer.validated_data["observacion"],
            )
        except AdopcionPermisoError as exc:
            return Response({"detalle": error(str(exc))}, status=403)
        except AdopcionError as exc:
            return Response({"detalle": error(str(exc))}, status=400)
        return Response({
            "id_solicitud_adopcion": solicitud.pk,
            "estado": etiqueta(solicitud.estado_adopcion.nombre),
        })

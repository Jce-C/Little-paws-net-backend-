"""Endpoints JSON para solicitudes de adopcion."""

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SolicitudAdopcion
from .serializers import SolicitudAdopcionCrearSerializer, representar_solicitud
from .services import AdopcionError, crear_solicitud_adopcion


def solicitudes_visibles(usuario):
    return (
        SolicitudAdopcion.objects.select_related(
            "mascota",
            "fundacion__entidad",
            "estado_solicitud",
        )
        .filter(
            Q(usuario_solicitante=usuario)
            | Q(
                fundacion__entidad__entidadmiembro__usuario=usuario,
                fundacion__entidad__entidadmiembro__fecha_salida__isnull=True,
            )
        )
        .distinct()
    )


class SolicitudAdopcionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        solicitudes = solicitudes_visibles(request.user).order_by("-fecha_solicitud", "-pk")
        mascota_id = request.query_params.get("id_mascota")
        if mascota_id:
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
                observacion_solicitante=datos.get("observacion_solicitante", ""),
                archivo_soporte=datos.get("archivo_soporte"),
            )
        except AdopcionError as exc:
            return Response({"detalle": str(exc)}, status=400)
        solicitud = SolicitudAdopcion.objects.select_related(
            "mascota",
            "fundacion__entidad",
            "estado_solicitud",
        ).get(pk=solicitud.pk)
        return Response(representar_solicitud(solicitud), status=201)


class SolicitudAdopcionDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, solicitud_id):
        solicitud = solicitudes_visibles(request.user).filter(pk=solicitud_id).first()
        if solicitud is None:
            return Response({"detalle": "Solicitud inexistente o sin acceso"}, status=404)
        return Response(representar_solicitud(solicitud, incluir_historial=True))

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from animals.models import CustodiaMascota, Mascota
from core.models import ValorMaestro
from .models import SolicitudAdopcion
from .services import AdopcionError, resolver_solicitud


class MascotasAdopcionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        disponibles = Mascota.objects.select_related("raza__especie").filter(
            estado_mascota__tipo__nombre="estado_mascota",
            estado_mascota__nombre="En adopción",
            custodiamascota__fecha_fin__isnull=True,
        ).distinct()[:100]
        return Response([
            {
                "id_mascota": m.pk, "nombre": m.nombre,
                "raza": m.raza.nombre, "especie": m.raza.especie.nombre,
            }
            for m in disponibles
        ])


class SolicitudCrearSerializer(serializers.Serializer):
    id_mascota = serializers.IntegerField(min_value=1)
    observaciones = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class SolicitudCrearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = SolicitudCrearSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        mascota = Mascota.objects.filter(pk=s.validated_data["id_mascota"]).first()
        if mascota is None or mascota.estado_mascota.nombre != "En adopción":
            return Response({"detalle": "Mascota no disponible"}, status=400)
        if not CustodiaMascota.objects.filter(mascota=mascota, fecha_fin__isnull=True).exists():
            return Response({"detalle": "Custodia no confirmada"}, status=400)
        if SolicitudAdopcion.objects.filter(
            mascota=mascota, usuario_adoptante=request.user,
            estado_adopcion__nombre="Pendiente",
        ).exists():
            return Response({"detalle": "Ya tienes una solicitud pendiente"}, status=400)
        solicitud = SolicitudAdopcion.objects.create(
            mascota=mascota,
            usuario_adoptante=request.user,
            estado_adopcion=ValorMaestro.objects.get(tipo__nombre="estado_adopcion", nombre="Pendiente"),
            observaciones=s.validated_data.get("observaciones", ""),
        )
        return Response({"id_solicitud_adopcion": solicitud.pk}, status=status.HTTP_201_CREATED)


class SolicitudResolverSerializer(serializers.Serializer):
    id_fundacion = serializers.IntegerField(min_value=1)
    aprobar = serializers.BooleanField()
    observacion = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class SolicitudResolverView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, solicitud_id):
        s = SolicitudResolverSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            solicitud = resolver_solicitud(
                solicitud_id=solicitud_id,
                fundacion_id=s.validated_data["id_fundacion"],
                usuario_actor_id=request.user.pk,
                aprobar=s.validated_data["aprobar"],
                observacion=s.validated_data.get("observacion", ""),
            )
        except AdopcionError as exc:
            return Response({"detalle": str(exc)}, status=400)
        return Response({"id_solicitud_adopcion": solicitud.pk, "estado": solicitud.estado_adopcion.nombre})

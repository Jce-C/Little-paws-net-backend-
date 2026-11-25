from seguridad.participacion import Participacion
from seguridad.servicios import auditar
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from animals.models import CustodiaMascota, Mascota
from core.models import ValorMaestro
from .models import SolicitudAdopcion
from .services import AdopcionError, resolver_solicitud


class MascotasAdopcionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from seguridad.models import BajaAdministrativa
        bajas=BajaAdministrativa.objects.filter(tipo='entidades',activo=False).values('objeto_id')
        from .consultas import disponibles_adopcion
        disponibles = disponibles_adopcion().select_related('especie','raza__especie')[:100]
        return Response([
            {
                "id_mascota": m.pk, "nombre": m.nombre,
                "raza": m.raza_nombre, "especie": m.especie_nombre,
            }
            for m in disponibles
        ])


class SolicitudCrearSerializer(serializers.Serializer):
    id_mascota = serializers.IntegerField(min_value=1)
    observaciones = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class SolicitudCrearView(APIView):
    permission_classes = [IsAuthenticated, Participacion]
    serializer_class = SolicitudCrearSerializer

    @transaction.atomic
    def post(self, request):
        s = self.serializer_class(data=request.data)
        s.is_valid(raise_exception=True)
        mascota = Mascota.objects.select_for_update().filter(pk=s.validated_data["id_mascota"]).first()
        from .consultas import disponibles_adopcion
        if mascota is not None and not disponibles_adopcion().filter(pk=mascota.pk).exists():
            return Response({'detalle':'Mascota no disponible'},status=400)
        if mascota is None or mascota.estado_mascota.nombre != "En adopción":
            return Response({"detalle": "Mascota no disponible"}, status=400)
        fundacion_id = CustodiaMascota.objects.filter(
            mascota=mascota, fecha_fin__isnull=True,
        ).values_list("fundacion_id", flat=True).first()
        if fundacion_id is None:
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
        if "evaluacion" in s.validated_data:
            from .questionnaire import guardar
            guardar(solicitud, fundacion_id, s.validated_data["evaluacion"])
        from .models import HistorialEstadoAdopcion
        HistorialEstadoAdopcion.objects.create(solicitud=solicitud, estado_nuevo=solicitud.estado_adopcion, usuario_actor=request.user, observacion=s.validated_data.get('observaciones') or 'Solicitud registrada para revisión')
        # Keep the citizen API and the panel on the same audit/revision path.
        # Do not copy the applicant's private free text into the security log.
        auditar(
            request.user, "adopcion.participar", "adopcion", solicitud.pk,
            fundacion_id, operacion="solicitar-adopcion",
            mascota_id=mascota.pk, elemento_nombre=mascota.nombre,
            anterior=None, nuevo="Pendiente",
        )
        return Response({"id_solicitud_adopcion": solicitud.pk}, status=status.HTTP_201_CREATED)


from .questionnaire import EvaluacionEntrada
from seguridad.serializers import EntradaEstricta


class SolicitudEvaluacionEntrada(EntradaEstricta, serializers.Serializer):
    id_mascota = serializers.IntegerField(min_value=1)
    evaluacion = EvaluacionEntrada()


class SolicitudEvaluacionCrearView(SolicitudCrearView):
    serializer_class = SolicitudEvaluacionEntrada
    parser_classes = [JSONParser]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        return response


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

from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from commerce.models import EspacioPublicitario
from .models import Notificacion, TipoMaestro


class CatalogosView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tipos = TipoMaestro.objects.prefetch_related("valormaestro_set").filter(activo=True).order_by("nombre")
        return Response({
            tipo.nombre: [
                {"id": valor.pk, "nombre": valor.nombre}
                for valor in tipo.valormaestro_set.all()
            ]
            for tipo in tipos
        })


class PublicidadActivaView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ahora = timezone.now()
        espacios = EspacioPublicitario.objects.select_related("anunciante__entidad").filter(
            estado_publicidad__tipo__nombre="estado_publicidad",
            estado_publicidad__nombre="Aprobada",
            fecha_inicio__lte=ahora,
            fecha_fin__gt=ahora,
        ).order_by("id_espacio")[:30]
        from seguridad.flujos_views import publicidad_publica
        return Response([
            {
                "id_espacio": e.pk, "anunciante": e.anunciante.entidad.nombre,
                "url_destino": e.url_destino, "id_archivo": e.archivo_id,
            }
            for e in espacios
        ] + publicidad_publica())


class MisNotificacionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notificaciones = Notificacion.objects.filter(usuario=request.user).order_by("-fecha_creacion")[:100]
        return Response([
            {"id_notificacion": n.pk, "contenido": n.contenido,
             "fecha_creacion": n.fecha_creacion, "fecha_lectura": n.fecha_lectura}
            for n in notificaciones
        ])


class LeerNotificacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notificacion_id):
        actualizadas = Notificacion.objects.filter(
            pk=notificacion_id, usuario=request.user, fecha_lectura__isnull=True
        ).update(fecha_lectura=timezone.now())
        if actualizadas:
            return Response({"leida": True})
        if Notificacion.objects.filter(pk=notificacion_id, usuario=request.user).exists():
            return Response({"leida": True})
        return Response({"detalle": "Notificación inexistente"}, status=404)

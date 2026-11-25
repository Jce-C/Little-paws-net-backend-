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


class NotificacionPrivadaView(APIView):
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        return response


class MisNotificacionesView(NotificacionPrivadaView):
    def get(self, request):
        from rest_framework import serializers
        from seguridad.autorizacion import puede
        paged = request.query_params.get("paginado") == "1"
        before = request.query_params.get("antes")
        before = serializers.IntegerField(min_value=1, max_value=2147483647).run_validation(before) if before is not None else None
        rows = Notificacion.objects.filter(usuario=request.user).select_related("tipo_notificacion", "solicitud_adopcion").defer("solicitud_adopcion__observaciones").order_by("-pk")
        if before is not None:
            rows = rows.filter(pk__lt=before)
        limit = 20 if paged else 100
        rows = list(rows[:limit + 1])
        more = len(rows) > limit
        rows = rows[:limit]
        adoption_allowed = puede(request.user, "adopcion.participar") if any(n.solicitud_adopcion_id for n in rows) else False
        result = []
        for n in rows:
            destination = None
            if adoption_allowed and n.solicitud_adopcion_id and n.solicitud_adopcion.usuario_adoptante_id == request.user.pk:
                destination = {"tipo": "solicitud_adopcion", "id": n.solicitud_adopcion_id}
            result.append({"id_notificacion": n.pk, "contenido": n.contenido,
                           "tipo": n.tipo_notificacion.nombre, "destino": destination,
                           "fecha_creacion": n.fecha_creacion, "fecha_lectura": n.fecha_lectura})
        return Response({"results": result, "next_cursor": str(rows[-1].pk) if more else None} if paged else result)


class LeerNotificacionView(NotificacionPrivadaView):
    def post(self, request, notificacion_id):
        from django.shortcuts import get_object_or_404
        row = get_object_or_404(Notificacion.objects.filter(usuario=request.user), pk=notificacion_id)
        Notificacion.objects.filter(pk=row.pk, fecha_lectura__isnull=True).update(fecha_lectura=timezone.now())
        row.refresh_from_db(fields=["fecha_lectura"])
        return Response({"leida": True, "fecha_lectura": row.fecha_lectura})

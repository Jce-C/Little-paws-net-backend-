"""Consultas mínimas para el reporte y seguimiento ciudadano móvil."""
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from core.models import Ciudad, ValorMaestro
from .models import Reporte
from .public_reports import public_report_page


class PublicReportsThrottle(AnonRateThrottle):
    # La lectura de páginas no consume el presupuesto de acceso/registro.
    scope = "public_reports"
    rate = "60/minute"


class ReportesPublicosPaginadosView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PublicReportsThrottle]

    def get(self, request):
        return Response(public_report_page(request.query_params))


class OpcionesReporteView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def get(self, request):
        query = request.query_params.get("ciudad", "").strip()[:100]
        ciudades = Ciudad.objects.none()
        if len(query) >= 2:
            ciudades = Ciudad.objects.filter(activo=True, nombre__icontains=query).order_by("nombre", "departamento", "pk")[:30]
        return Response({
            "tipos": list(ValorMaestro.objects.filter(tipo__nombre="tipo_reporte", tipo__activo=True).order_by("nombre").values("id_valor_maestro", "nombre")),
            "ciudades": list(ciudades.values("id_ciudad", "nombre", "departamento")),
        })


class MisReportesView(APIView):
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        return response

    def get(self, request):
        from seguridad.autorizacion import exigir
        exigir(request.user, 'reportes.participar')
        reportes = Reporte.objects.filter(usuario_reportante=request.user).select_related(
            "tipo_reporte", "estado_reporte", "ciudad", "foto_ciudadana", "casorescate__estado_caso", "casorescate__fundacion__entidad",
        ).defer("foto_ciudadana__contenido").order_by("-fecha_creacion", "-pk")[:100]
        from .photo_views import foto_descriptor
        rows = []
        for reporte in reportes:
            caso = getattr(reporte, "casorescate", None)
            rows.append({
                "id_reporte": reporte.pk, "foto":foto_descriptor(reporte),
                "tipo": reporte.tipo_reporte.nombre,
                "estado": reporte.estado_reporte.nombre,
                "descripcion": reporte.descripcion,
                "fecha_creacion": reporte.fecha_creacion,
                "ciudad": reporte.ciudad.nombre if reporte.ciudad else "",
                "caso": None if caso is None else {
                    "id_caso": caso.pk,
                    "estado": caso.estado_caso.nombre,
                    "fundacion": caso.fundacion.entidad.nombre,
                    "fecha_aceptacion": caso.fecha_aceptacion,
                },
            })
        return Response(rows)

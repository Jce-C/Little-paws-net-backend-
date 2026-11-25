"""Read only sanitized photos of reports that remain publicly visible."""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from .models import FotoReporte
from .public_reports import visible_reports

class FotoReporteView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, reporte_id):
        get_object_or_404(visible_reports(), pk=reporte_id)
        foto = get_object_or_404(FotoReporte, reporte_id=reporte_id)
        response = HttpResponse(bytes(foto.contenido), content_type='image/webp')
        response['Cache-Control'] = 'no-store'
        response['X-Content-Type-Options'] = 'nosniff'
        return response

def foto_descriptor(reporte):
    photo = getattr(reporte, 'foto_ciudadana', None)
    return None if photo is None else {'url': f'/api/reportes/{reporte.pk}/foto/', 'ancho': photo.ancho, 'alto': photo.alto, 'bytes': photo.tamano_bytes}

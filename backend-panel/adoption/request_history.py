"""A request is visible to its applicant; administrative decisions keep their existing route."""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SolicitudAdopcion
from seguridad.autorizacion import exigir
from .consultas import disponibles_adopcion
from animals.medical_thumbnail import miniatura

def resumen(row, include_photo=True):
    return {'id_solicitud_adopcion': row.pk, 'mascota_id': row.mascota_id,
      'mascota__nombre': row.mascota.nombre, 'estado_adopcion__nombre': row.estado_adopcion.nombre,
      'fecha_solicitud': row.fecha_solicitud, 'fecha_resolucion': row.fecha_resolucion,
      'motivo_decision': row.observaciones if row.fecha_resolucion else '',
      'foto_miniatura': miniatura(row.mascota) if include_photo else None}

class SolicitudDetalleView(APIView):
    permission_classes = [IsAuthenticated]
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        return response
    def get(self, request, solicitud_id):
        exigir(request.user,"adopcion.participar")
        row = get_object_or_404(SolicitudAdopcion.objects.select_related('mascota', 'estado_adopcion'), pk=solicitud_id, usuario_adoptante=request.user)
        data = resumen(row)
        from .questionnaire import consultar
        data['evaluacion'] = consultar(row.pk)
        data['historial'] = list(row.historialestadoadopcion_set.select_related('estado_nuevo').order_by('fecha_cambio', 'pk').values('fecha_cambio', 'estado_nuevo__nombre', 'observacion'))
        response = Response(data); response['Cache-Control'] = 'no-store'; return response

class MisSolicitudesView(APIView):
    permission_classes=[IsAuthenticated]
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        return response
    def get(self,request):
        exigir(request.user,"adopcion.participar")
        from rest_framework import serializers
        before=request.query_params.get('antes')
        before=serializers.IntegerField(min_value=1,max_value=2147483647).run_validation(before) if before is not None else None
        rows=SolicitudAdopcion.objects.filter(usuario_adoptante=request.user).select_related('mascota','estado_adopcion').order_by('-pk')
        if before is not None:rows=rows.filter(pk__lt=before)
        rows=list(rows[:21]);more=len(rows)>20;rows=rows[:20]
        response=Response({'results':[resumen(row) for row in rows], 'next_cursor':str(rows[-1].pk) if more else None});response['Cache-Control']='no-store';return response

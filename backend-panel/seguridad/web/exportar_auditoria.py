import csv
from django.http import StreamingHttpResponse
from django.utils import timezone
from seguridad.autorizacion import exigir
from seguridad.servicios import auditar

class Echo:
    def write(self,value):return value

def celda(value):
    text=str(value or '')
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) or text.startswith(('\t','\r')) else text

def exportar(request,qs):
    exigir(request.user,'auditoria.exportar')
    # Explicit, bounded export of the same filtered records; never export raw JSON.
    from seguridad.models import EventoSeguridad
    ceiling=EventoSeguridad.objects.order_by('-pk').values_list('pk',flat=True).first() or 0
    qs=qs.filter(pk__lte=ceiling)
    total=qs.count();limit=10000
    def rows():
        writer=csv.writer(Echo());yield '\ufeff'+writer.writerow(['ID','Fecha ISO','Actor ID','Actor','Roles registrados','Acción','Recurso','Objeto ID','Resultado'])
        for e in qs[:limit].iterator(chunk_size=200):
            meta=e.datos.get('_contexto',{})
            yield writer.writerow([celda(v) for v in [e.pk,timezone.localtime(e.fecha).isoformat(),e.actor_id,meta.get('actor_nombre') or getattr(e.actor,'nombre',''),', '.join(meta.get('roles_vigentes',[])),e.accion,e.recurso,e.objeto_id,meta.get('resultado','NO_REGISTRADO')]])
    auditar(request.user,'auditoria.exportar','auditoria',motivo='Exportación solicitada',filas=min(total,limit),limite=limit)
    response=StreamingHttpResponse(rows(),content_type='text/csv; charset=utf-8');response['Content-Disposition']='attachment; filename="auditoria.csv"';response['Cache-Control']='no-store';return response

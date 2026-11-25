"""Create a private, verified copy; this command never deletes historical events."""
import gzip,json,hashlib
from pathlib import Path
from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand,CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from seguridad.models import EventoSeguridad
from seguridad.auditoria_contexto import seguro

class Command(BaseCommand):
    help='Inspecciona o archiva una copia privada de auditoría, sin eliminar registros.'
    def add_arguments(self,parser):
        parser.add_argument('--antes',help='Fecha ISO con zona horaria. Por defecto, 365 días de antigüedad.')
        parser.add_argument('--dias',type=int,default=365)
        parser.add_argument('--escribir',action='store_true')
    def handle(self,*args,**options):
        if options['dias']<1:raise CommandError('Los días deben ser positivos.')
        cutoff=parse_datetime(options['antes']) if options['antes'] else timezone.now()-timedelta(days=options['dias'])
        if cutoff is None or timezone.is_naive(cutoff):raise CommandError('Usa una fecha ISO con zona horaria.')
        qs=EventoSeguridad.objects.filter(fecha__lt=cutoff).order_by('pk');count=qs.count()
        sample=list(qs.order_by('-pk').values_list('datos',flat=True)[:100])
        average=round(sum(len(json.dumps(v,default=str,ensure_ascii=False).encode('utf-8')) for v in sample)/max(1,len(sample)))
        self.stdout.write(json.dumps({'muestra':len(sample),'muestreo':'ultimos eventos del conjunto filtrado; no predice el tamaño de eventos futuros','promedio_json_bytes':average,'estimacion_json_bytes':average*count,'eventos':count,'antes':cutoff.isoformat(),'politica':'conservacion sin borrado','indices':['fecha','actor+fecha','recurso+fecha']}))
        if not options['escribir']:return
        root=(Path(settings.LPN_PRIVATE_ROOT)/'auditoria').resolve();root.mkdir(parents=True,exist_ok=True)
        path=root/('auditoria-'+timezone.now().strftime('%Y%m%dT%H%M%S%f')+'.jsonl.gz')
        written=0
        with gzip.open(path,'xt',encoding='utf-8') as f:
            for row in qs.values('pk','actor_id','accion','recurso','objeto_id','entidad_id','motivo','datos','fecha').iterator(chunk_size=500):
                row['datos']=seguro(row['datos']);f.write(json.dumps(row,ensure_ascii=False,default=str)+'\n');written+=1
        hasher=hashlib.sha256()
        with path.open('rb') as archive:
            for chunk in iter(lambda:archive.read(1024*1024),b''):hasher.update(chunk)
        digest=hasher.hexdigest()
        manifest={'filas':written,'sha256':digest,'bytes':path.stat().st_size,'antes':cutoff.isoformat(),'registros_eliminados':0}
        path.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        self.stdout.write(json.dumps(manifest))

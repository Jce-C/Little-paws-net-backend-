import json
from django.core.management.base import BaseCommand,CommandError
from core.models import Ciudad,ValorMaestro
from animals.models import Especie,Raza
class Command(BaseCommand):
    help='Comprueba referencias mínimas para formularios, sin crear datos de negocio.'
    def add_arguments(self,parser):parser.add_argument('--estricto',action='store_true')
    def handle(self,*args,**options):
        counts={'ciudades_activas':Ciudad.objects.filter(activo=True).count(),'especies_activas':Especie.objects.filter(activo=True).count(),'razas_activas':Raza.objects.filter(activo=True,especie__activo=True).count()}
        missing=[k for k,v in counts.items() if not v]
        for tipo in ('estado_mascota','tipo_reporte','estado_reporte','estado_verificacion','categoria_producto','tipo_producto'):
            if not ValorMaestro.objects.filter(tipo__nombre=tipo).exists():missing.append(tipo)
        self.stdout.write(json.dumps({'catalogos':counts,'faltantes':missing,'listo_para_registros':not missing},ensure_ascii=False))
        if missing and options['estricto']:raise CommandError('Faltan referencias de producción.')

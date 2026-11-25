"""Carga referencias reales sin crear personas, mascotas ni transacciones."""
import json,unicodedata,re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Ciudad
from animals.models import Especie,Raza

def clave(departamento,nombre):
    d,n=normalizar(departamento),normalizar(nombre)
    return (d,'bogotadc' if d=='bogotadc' and n in ('bogota','bogotadc') else n)

def normalizar(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())

class Command(BaseCommand):
    help='Carga idempotente de ciudades DIVIPOLA y referencias iniciales de perros/gatos. No altera valores existentes.'
    @transaction.atomic
    def handle(self,*args,**options):
        data=json.loads((Path(__file__).resolve().parents[2]/'data/ciudades_divipola.json').read_text(encoding='utf-8'))
        existentes={clave(c.departamento,c.nombre):c for c in Ciudad.objects.all()}
        codes=set(Ciudad.objects.exclude(codigo_divipola=None).values_list('codigo_divipola',flat=True));n=0;pendientes=[]
        for row in data['ciudades']:
            if row['codigo'] in codes:continue
            key=clave(row['departamento'],row['nombre'])
            if key in existentes:
                c=existentes[key]
                if not c.codigo_divipola:c.codigo_divipola=row['codigo'];c.save(update_fields=['codigo_divipola'])
            else:pendientes.append(Ciudad(nombre=row['nombre'],departamento=row['departamento'],codigo_divipola=row['codigo']));n+=1
            codes.add(row['codigo'])
        Ciudad.objects.bulk_create(pendientes,batch_size=200)
        razas={'Perro':['Mestizo','Raza no determinada','Labrador retriever','Golden retriever','Pastor alemán','Bulldog','Poodle','Chihuahua','Beagle','Schnauzer','Shih tzu','Husky siberiano','Dálmata','Bóxer'], 'Gato':['Mestizo','Raza no determinada','Siamés','Persa','Maine coon','Bengalí','Ragdoll','British shorthair']}
        nr=0
        for nombre,nombres in razas.items():
            e,_=Especie.objects.get_or_create(nombre=nombre)
            for name in nombres:
                _,creada=Raza.objects.get_or_create(especie=e,nombre=name);nr+=creada
        self.stdout.write(json.dumps({'ciudades_creadas':n,'ciudades_total':Ciudad.objects.count(),'razas_creadas':nr,'razas_total':Raza.objects.count(),'fuente':data['fuente'],'datos_de_negocio_creados':0},ensure_ascii=False))

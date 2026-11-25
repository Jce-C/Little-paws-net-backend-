from rest_framework.exceptions import ValidationError
from .models import Raza,Especie

def identificar(datos,instancia=None):
    """Known breed implies species; unknown animals do not require fake taxonomy."""
    d=dict(datos)
    raza_id=d.get('raza_id',getattr(instancia,'raza_id',None))
    especie_id=d.get('especie_id',getattr(instancia,'especie_id',None))
    if 'raza_id' in d and d['raza_id'] and 'especie_id' not in d:especie_id=None
    descripcion=d.get('descripcion_especie',getattr(instancia,'descripcion_especie','')).strip()
    if raza_id:
        raza=Raza.objects.filter(pk=raza_id,activo=True,especie__activo=True).first()
        if not raza:raise ValidationError({'raza_id':'Selecciona una raza activa.'})
        if especie_id and especie_id!=raza.especie_id:raise ValidationError({'raza_id':'La raza no corresponde a la especie elegida.'})
        especie_id=raza.especie_id
    if especie_id and not Especie.objects.filter(pk=especie_id,activo=True).exists():raise ValidationError({'especie_id':'Selecciona una especie activa.'})
    if not especie_id and not descripcion:raise ValidationError({'descripcion_especie':'Selecciona una especie o describe el animal si no está en el catálogo.'})
    d.update(raza_id=raza_id,especie_id=especie_id,descripcion_especie=descripcion)
    return d

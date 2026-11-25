"""Referencias de producción con permisos, versiones y auditoría compartidos."""
import hashlib,json
from django import forms
from django.db import transaction
from rest_framework.exceptions import ValidationError,NotFound
from core.models import Ciudad
from animals.models import Especie,Raza
from .autorizacion import exigir,invalidar
from .servicios import auditar,bloqueo_seguridad
MODELOS={'ciudades':Ciudad,'especies':Especie,'razas':Raza}
CAMPOS={'ciudades':['nombre','departamento','codigo_divipola','activo'],'especies':['nombre','descripcion','activo'],'razas':['nombre','especie','activo']}

def version(obj):return hashlib.sha256(json.dumps({k:str(getattr(obj,k)) for k in CAMPOS[next(k for k,v in MODELOS.items() if isinstance(obj,v))]},sort_keys=True).encode()).hexdigest()

def formulario(tipo,datos=None,obj=None):
    F=forms.modelform_factory(MODELOS[tipo],fields=CAMPOS[tipo]);f=F(datos,instance=obj)
    for name,field in f.fields.items():
        field.label={'codigo_divipola':'Código DIVIPOLA','activo':'Disponible para nuevos registros','especie':'Especie'}.get(name,field.label)
        if name=='especie':
            field.queryset=Especie.objects.filter(activo=True).order_by('nombre')
            field.label_from_instance=lambda obj:obj.nombre
    return f

@transaction.atomic
def guardar(actor,tipo,datos,pk=None,firma=None):
    exigir(actor,'catalogos.editar' if pk else 'catalogos.crear');bloqueo_seguridad()
    exigir(actor,'catalogos.editar' if pk else 'catalogos.crear')
    if tipo not in MODELOS:raise ValidationError('Catálogo no disponible.')
    obj=MODELOS[tipo].objects.select_for_update().filter(pk=pk).first() if pk else None
    if pk and obj is None:raise NotFound('Registro no disponible.')
    if obj and firma!=version(obj):raise ValidationError('El catálogo cambió. Recarga antes de guardar.')
    before={k:str(getattr(obj,k)) for k in CAMPOS[tipo]} if obj else None
    f=formulario(tipo,datos,obj)
    if not f.is_valid():raise ValidationError({k:list(v) for k,v in f.errors.items()})
    obj=f.save();auditar(actor,'catalogos.editar' if pk else 'catalogos.crear','catalogos',obj.pk,motivo=tipo,anterior=before,nuevo={k:str(getattr(obj,k)) for k in CAMPOS[tipo]});invalidar()
    return obj

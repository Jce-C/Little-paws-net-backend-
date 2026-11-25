from django.db.models import Q
from animals.models import Mascota
from seguridad.autorizacion import motor

def mascotas_visibles(usuario,entidad=None):
    m=motor(usuario)
    if m.base('mascotas.ver'):return Mascota.objects.all()
    from adoption.consultas import disponibles_adopcion
    publicas=Q(pk__in=disponibles_adopcion().values('pk'))
    return Mascota.objects.filter(Q(dueno=usuario)|publicas|Q(custodiamascota__fundacion_id=entidad,custodiamascota__fecha_fin__isnull=True)).distinct()

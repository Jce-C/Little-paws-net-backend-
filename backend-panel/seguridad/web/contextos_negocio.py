from core.models import EntidadVerificable
from seguridad.autorizacion import motor,principal_de

def organizaciones_para(actor,op):
    m=motor(actor)
    qs=EntidadVerificable.objects.exclude(pk__in=m.bajas_entidad).order_by('nombre')
    if op.permiso:return [e for e in qs if m.base(op.permiso,e.pk)]
    if 'verificaciones' in op.url:return [e for e in qs if principal_de(actor,e.pk) or m.base('entidades.editar')]
    if 'transferencias' in op.url:
        from seguridad.models import TransferenciaResponsabilidad
        ids=TransferenciaResponsabilidad.objects.filter(sucesor__usuario=actor,estado='PENDIENTE').values_list('entidad_id',flat=True)
        return list(qs.filter(pk__in=ids))
    return [e for e in qs if e.pk in m.miembros or m.base('entidades.ver')]

def preparar_contexto(request,area,operaciones):
    """Context belongs to the selected operation, not a hidden header dependency."""
    key=request.GET.get('accion');op=operaciones.get(key)
    if area!='organizaciones' or not op or op.area!=area:return
    raw=request.POST.get('organizacion',request.GET.get('organizacion',''))
    if raw:
        from rest_framework.exceptions import PermissionDenied
        validos={e.pk for e in organizaciones_para(request.user,op)}
        if not str(raw).isdigit() or int(raw) not in validos:raise PermissionDenied('Organización no disponible para esta operación.')
        request.panel={**request.panel,'entidad_id':int(raw)}
    # A form entered without an explicit organization starts unselected.
    elif '{entidad}' in op.url or key=='resolver-transferencia':
        request.panel={**request.panel,'entidad_id':None}

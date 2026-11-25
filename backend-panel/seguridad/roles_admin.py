import hashlib,json
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from core.models import Rol,Permiso,RolPermiso,UsuarioRol,EntidadMiembroRol
from .autorizacion import exigir
from .administracion_segura import delegables,validar_rol
from .politicas import POLITICAS

def version_rol(rol):
    ids=sorted(x.permiso_id for x in rol.rolpermiso_set.all())
    return hashlib.sha256(json.dumps([rol.pk,rol.nombre,rol.descripcion,rol.ambito,rol.activo,rol.entidad_id,ids],sort_keys=True).encode()).hexdigest()

@transaction.atomic
def guardar_permisos(actor,rol,ids):
    from .servicios import bloqueo_seguridad,auditar,limpiar_asignaciones
    bloqueo_seguridad();exigir(actor,'roles.editar');rol=Rol.objects.select_for_update().get(pk=rol.pk)
    permisos=list(Permiso.objects.filter(pk__in=ids,activo=True,recurso__activo=True))
    if len(ids)!=len(set(ids)) or len(permisos)!=len(ids) or any(p.codigo not in POLITICAS for p in permisos):raise ValidationError('Selecciona permisos activos e implementados.')
    validar_rol(actor,rol,rol.entidad_id);delegables(actor,[p.codigo for p in permisos],rol.entidad_id)
    antes=list(RolPermiso.objects.filter(rol=rol).values_list('permiso__codigo',flat=True))
    RolPermiso.objects.filter(rol=rol).exclude(permiso_id__in=ids).delete()
    for p in permisos:RolPermiso.objects.get_or_create(rol=rol,permiso=p)
    for pk in set(UsuarioRol.objects.filter(rol=rol).values_list('usuario_id',flat=True))|set(EntidadMiembroRol.objects.filter(rol=rol).values_list('miembro__usuario_id',flat=True)):limpiar_asignaciones(pk)
    auditar(actor,'rol.permisos','roles',rol.pk,anterior=antes,nuevo=[p.codigo for p in permisos],elemento_nombre=rol.nombre)
    return rol

@transaction.atomic
def guardar_rol(actor,datos,instancia=None,version=None):
    from .servicios import bloqueo_seguridad,auditar
    bloqueo_seguridad();exigir(actor,'roles.editar' if instancia else 'roles.crear')
    datos=dict(datos);ids=datos.pop('permisos',None)
    if instancia:instancia=Rol.objects.select_for_update().get(pk=instancia.pk);validar_rol(actor,instancia,instancia.entidad_id)
    if instancia and version is not None and version!=version_rol(instancia):raise ValidationError('El rol cambió en otra sesión. Reabre el formulario antes de guardar.')
    entity=datos.get('entidad',getattr(instancia,'entidad',None));entity_id=getattr(entity,'pk',None)
    scope=datos.get('ambito',getattr(instancia,'ambito','GLOBAL'))
    if scope=='GLOBAL' and entity:raise ValidationError('Un rol de plataforma no se vincula a una organización.')
    if entity_id:delegables(actor,[],entity_id)
    if instancia and entity_id!=instancia.entidad_id and EntidadMiembroRol.objects.filter(rol=instancia).exclude(miembro__entidad_id=entity_id).exists():raise ValidationError('Reasigna las dependencias antes de cambiar la organización del rol.')
    if instancia and 'activo' in datos and datos['activo']!=instancia.activo:
        exigir(actor,'roles.restaurar' if datos['activo'] else 'roles.desactivar')
        from .models import BajaAdministrativa
        if datos['activo'] and BajaAdministrativa.objects.filter(tipo='roles',objeto_id=instancia.pk,activo=False).exists():raise ValidationError('Utiliza la restauración confirmada para reactivar este rol.')
    permisos=[] if ids is None else list(Permiso.objects.filter(pk__in=ids,activo=True,recurso__activo=True))
    if ids is not None:
        if len(ids)!=len(set(ids)) or len(ids)!=len(permisos) or any(p.codigo not in POLITICAS for p in permisos):raise ValidationError('Selecciona permisos activos e implementados.')
        delegables(actor,[p.codigo for p in permisos],entity_id)
    serial=lambda v:getattr(v,'pk',v)
    antes={k:serial(getattr(instancia,k)) for k in datos} if instancia else None
    obj=instancia or Rol()
    for key,value in datos.items():setattr(obj,key,value)
    obj.save()
    if ids is not None:
        RolPermiso.objects.filter(rol=obj).exclude(permiso_id__in=ids).delete()
        for p in permisos:RolPermiso.objects.get_or_create(rol=obj,permiso=p)
    auditar(actor,'roles.editar' if instancia else 'roles.crear','roles',obj.pk,anterior=antes,nuevo={k:serial(v) for k,v in datos.items()},permisos=[p.codigo for p in permisos] if ids is not None else None,elemento_nombre=obj.nombre)
    return obj

"""Atomic multiple-role assignment shared by HTML and JSON interfaces."""
import hashlib,json
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError,PermissionDenied
from accounts.models import Usuario
from core.models import Rol,UsuarioRol,EntidadMiembro,EntidadMiembroRol
from .models import ExcepcionPermiso
from .autorizacion import exigir,motor
from .servicios import asignar_global,auditar,bloqueo_seguridad,motivo_obligatorio

def firma_persona(usuario,entidad,tab):
    if tab=='usuarios':
        datos=list(EntidadMiembroRol.objects.filter(miembro__usuario=usuario,miembro__entidad_id=entidad,fecha_revocacion__isnull=True).order_by('rol_id').values_list('rol_id',flat=True)) if entidad else list(UsuarioRol.objects.filter(usuario=usuario,fecha_revocacion__isnull=True).order_by('rol_id').values_list('rol_id',flat=True))
    else:
        datos=list(ExcepcionPermiso.objects.filter(usuario=usuario,contexto_id=entidad or 0).order_by('permiso_id').values('permiso_id','efecto','motivo','expira'))
    return hashlib.sha256(json.dumps(datos,sort_keys=True,default=str).encode()).hexdigest()


@transaction.atomic
def guardar_roles(actor,usuario_id,roles,entidad=None,version=None,motivo='',incorporar=False,activar_inactivos=False):
    bloqueo_seguridad()
    motivo=motivo_obligatorio(motivo)
    exigir(actor,'roles.asignar')
    usuario=get_object_or_404(Usuario.objects.select_for_update(),pk=int(usuario_id),is_active=True)
    entidad=int(entidad) if entidad else None
    from core.models import EntidadVerificable
    if entidad and not EntidadVerificable.objects.filter(pk=entidad).exists():raise ValidationError('Organización no disponible.')
    if entidad in motor(actor).bajas_entidad:raise ValidationError('Restaura la entidad antes de modificarla.')
    if version!=firma_persona(usuario,entidad,'usuarios'):
        raise ValidationError('Los roles de esta persona cambiaron. Recarga antes de guardar.')
    ids={int(x) for x in roles}
    from django.db.models import Q
    # The assignment sets the context; a role's suggested scope is not a
    # whitelist of assignable profiles. Organization-owned roles remain local.
    elegibles=Rol.objects.filter(Q(entidad__isnull=True)|Q(entidad_id=entidad))
    if ids-set(elegibles.values_list('pk',flat=True)):
        raise ValidationError('Uno de los roles no pertenece a este contexto.')
    from .models import BajaAdministrativa
    from .administracion_segura import validar_rol
    for rol in elegibles.filter(pk__in=ids,activo=False).select_for_update():
        if not activar_inactivos:raise ValidationError('Confirma activar los roles inactivos seleccionados.')
        exigir(actor,'roles.restaurar')
        validar_rol(actor,rol,entidad)
        if BajaAdministrativa.objects.filter(tipo='roles',objeto_id=rol.pk,activo=False).exists():raise ValidationError('Restaura el rol archivado antes de asignarlo.')
        rol.activo=True;rol.save(update_fields=['activo'])
        auditar(actor,'roles.restaurar','roles',rol.pk,motivo=motivo,anterior={'activo':False},nuevo={'activo':True})
    elegibles=elegibles.filter(activo=True)
    miembro=None
    if entidad:
        from seguridad.administracion_segura import administrador_total
        ma=motor(actor)
        if not administrador_total(actor) and not (entidad in ma.miembros and (ma.base('miembros.roles',entidad) or ma.base('miembros.gestionar',entidad))):raise PermissionDenied('No administras este contexto.')
        miembro=EntidadMiembro.objects.filter(usuario=usuario,entidad_id=entidad,fecha_salida__isnull=True).first()
        if miembro is None:
            if not ids or not incorporar:raise ValidationError('Confirma incorporar a esta persona a la organización para asignarle roles.')
            if not administrador_total(actor):exigir(actor,'miembros.gestionar',entidad_id=entidad)
            miembro,_=EntidadMiembro.objects.update_or_create(usuario=usuario,entidad_id=entidad,defaults={'fecha_salida':None})
            auditar(actor,'miembro.incorporar','miembros',miembro.pk,entidad,motivo=motivo)
    from seguridad.administracion_segura import validar_rol
    for rol in elegibles:
        existe=(EntidadMiembroRol.objects.filter(miembro=miembro,rol=rol,fecha_revocacion__isnull=True).exists() if miembro else UsuarioRol.objects.filter(usuario=usuario,rol=rol,fecha_revocacion__isnull=True).exists())
        if existe!=(rol.pk in ids):
            validar_rol(actor,rol,entidad)
            if miembro:
                # Gestión central autorizada; no se falsifica el cargo principal.
                from django.utils import timezone
                EntidadMiembroRol.objects.update_or_create(miembro=miembro,rol=rol,defaults={'fecha_revocacion':None if rol.pk in ids else timezone.now()})
                auditar(actor,'rol_entidad.asignar' if rol.pk in ids else 'rol_entidad.revocar','miembros',miembro.pk,entidad,rol_id=rol.pk,anterior=existe,nuevo=rol.pk in ids)
            else:
                asignar_global(actor,usuario.pk,rol.pk,revocar=rol.pk not in ids,motivo=motivo)
    from seguridad.servicios import limpiar_asignaciones
    limpiar_asignaciones(usuario.pk)
    return {'guardado':True,'roles':list(ids),'version':firma_persona(usuario,entidad,'usuarios')}

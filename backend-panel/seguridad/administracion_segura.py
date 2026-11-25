"""Administrative authority, dependency inspection and confirmed, idempotent removal."""
import hashlib,json,uuid
from django.core import signing
from django.utils.translation import gettext as _t
from django.db import transaction
from django.db.models.deletion import Collector,ProtectedError,RestrictedError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied,ValidationError,NotFound
from accounts.models import Usuario
from core.models import Rol,Permiso,RolPermiso,EntidadVerificable,UsuarioRol,EntidadMiembroRol
from .autorizacion import motor,exigir,es_superusuario
from .models import BajaAdministrativa,OperacionAdministrativa

from commerce.models import Producto
MODELOS={'usuarios':Usuario,'roles':Rol,'entidades':EntidadVerificable,'productos':Producto}

def permiso_baja(tipo,accion):return ('producto' if tipo=='productos' else tipo)+'.'+('eliminar' if accion=='fisica' else accion)

def autorizar_baja(actor,tipo,accion,obj=None):
    exigir(actor,permiso_baja(tipo,accion),**({'entidad_id':obj.tienda_id} if tipo=='productos' and obj else {}))

def administrador_total(actor):
    m=motor(actor)
    return bool(m.usuario and m.usuario.is_active and (m.usuario.is_superuser or any(r['rol__codigo']=='ADMIN_SEGURIDAD' for r in m.globales)))

def delegables(actor,permisos,entidad=None):
    if administrador_total(actor):return
    m=motor(actor)
    if entidad is not None and entidad not in m.miembros:raise PermissionDenied('No administras esta organización.')
    if any(not m.base(c,entidad) for c in permisos):raise PermissionDenied('No puedes conceder capacidades superiores a tu autorización administrativa.')

def validar_rol(actor,rol,entidad=None):
    if rol.codigo=='ADMIN_SEGURIDAD' and not administrador_total(actor):raise PermissionDenied('Solo la administración de seguridad puede asignar este rol.')
    if rol.entidad_id and rol.entidad_id!=entidad:raise ValidationError('El rol pertenece a otra organización.')
    permisos=list(RolPermiso.objects.filter(rol=rol).values_list('permiso__codigo',flat=True))
    if entidad and rol.ambito=='ENTIDAD' and rol.delegable:
        from .servicios import es_responsable
        if es_responsable(actor,entidad) and motor(actor).base('miembros.roles',entidad):
            from .politicas import POLITICAS
            delegables(actor,[c for c in permisos if POLITICAS.get(c,('','',''))[2]=='GLOBAL'],entidad)
            return
    delegables(actor,permisos,entidad)

def dependencias(obj):
    result=[]
    for rel in obj._meta.related_objects:
        try:
            related=getattr(obj,rel.get_accessor_name())
            count=1 if rel.one_to_one else related.count()
        except ObjectDoesNotExist:count=0
        if count:result.append({'nombre':str(rel.related_model._meta.verbose_name_plural),'cantidad':count})
    if isinstance(obj,EntidadVerificable):
        from animals.models import Mascota
        from adoption.models import SolicitudAdopcion
        from rescue.models import Reporte
        from commerce.models import PedidoIniciado
        from funds.models import FondoExterno
        indirectas=[('Mascotas vinculadas (histórico)',Mascota.objects.filter(custodiamascota__fundacion_id=obj.pk).distinct()),('Adopciones vinculadas (histórico)',SolicitudAdopcion.objects.filter(mascota__custodiamascota__fundacion_id=obj.pk).distinct()),('Reportes vinculados',Reporte.objects.filter(casorescate__fundacion_id=obj.pk).distinct()),('Pedidos vinculados',PedidoIniciado.objects.filter(tienda_id=obj.pk)),('Fondos vinculados',FondoExterno.objects.filter(entidad_id=obj.pk))]
        for label,query in indirectas:
            count=query.count()
            if count:result.append({'nombre':label,'cantidad':count})
    return result

def estado(obj,tipo):
    baja=BajaAdministrativa.objects.filter(tipo=tipo,objeto_id=obj.pk).first()
    return {'activo':bool(getattr(obj,'is_active',getattr(obj,'activo',True))) and (baja is None or baja.activo),'eliminado':bool(baja and baja.eliminado)}

def datos_previa(actor,tipo,pk):
    if tipo not in MODELOS:raise ValidationError('Tipo de registro no disponible.')
    # Each available operation is authorized again on POST.
    m=motor(actor)
    obj=MODELOS[tipo].objects.filter(pk=pk).first()
    if obj is None:raise NotFound('Registro no disponible.')
    if tipo=='productos':autorizar_baja(actor,tipo,'eliminar',obj)
    elif not any(m.base(f'{tipo}.{a}') for a in ('eliminar','desactivar','restaurar')):raise PermissionDenied('No puedes administrar bajas en este módulo.')
    deps=dependencias(obj);current=estado(obj,tipo)
    permisos=list(RolPermiso.objects.filter(rol=obj).values_list('permiso__codigo',flat=True)) if tipo=='roles' else []
    usuarios=(UsuarioRol.objects.filter(rol=obj,fecha_revocacion__isnull=True).count()+EntidadMiembroRol.objects.filter(rol=obj,fecha_revocacion__isnull=True).count()) if tipo=='roles' else 0
    roles=list(UsuarioRol.objects.filter(usuario=obj,fecha_revocacion__isnull=True,rol__activo=True).values_list('rol__nombre',flat=True)) if tipo=='usuarios' else []
    if tipo=='usuarios':
        roles += [r.rol.nombre+' · '+r.miembro.entidad.nombre for r in EntidadMiembroRol.objects.filter(miembro__usuario=obj,miembro__fecha_salida__isnull=True,fecha_revocacion__isnull=True,rol__activo=True).select_related('rol','miembro__entidad')]
        from .models import ResponsableEntidad
        roles += ['Responsable principal · '+r.entidad.nombre for r in ResponsableEntidad.objects.filter(principal__usuario=obj,principal__fecha_salida__isnull=True).select_related('entidad')]
    identidad={campo:getattr(obj,campo,None) for campo in ('nombre','email','descripcion','ambito','entidad_id','estado_verificacion_id','is_active','activo','is_superuser','is_staff','tienda_id','estado_producto_id','precio','existencias')}
    firma=hashlib.sha256(json.dumps([obj.pk,identidad,current,deps,sorted(permisos),sorted(roles)],sort_keys=True,default=str).encode()).hexdigest()
    protegido=(tipo=='usuarios' and (obj.pk==actor.pk or obj.is_superuser)) or (tipo=='roles' and obj.sistema)
    return {'objeto':obj,'tipo_baja':tipo,'dependencias':deps,'estado_baja':current,'permisos_baja':permisos,'usuarios_asignados':usuarios,'roles_baja':roles,'firma_baja':firma,'protegido':protegido,'confirmacion_nombre':getattr(obj,'email',obj.nombre),'fisica_disponible':not deps and not protegido,'confirmacion_adicional':tipo!='productos' and bool(deps or usuarios or roles)}

def preparar_confirmacion(actor,tipo,pk):
    data=datos_previa(actor,tipo,pk)
    data['confirmacion_token']=signing.dumps({'actor':actor.pk,'tipo':tipo,'pk':pk,'firma':data['firma_baja'],'nonce':str(uuid.uuid4()),'entidad':data['objeto'].tienda_id if tipo=='productos' else None},salt='baja-administrativa')
    labels={'desactivar':_t('Desactivar'),'eliminar':_t('Eliminar lógicamente'),'restaurar':_t('Restaurar'),'fisica':_t('Borrar físicamente (solo sin dependencias)')}
    data['operaciones_baja']=[{'codigo':a,'nombre':labels[a]} for a in labels if (a in ('eliminar','fisica') and motor(actor).base('producto.eliminar',data['objeto'].tienda_id))] if tipo=='productos' else [{'codigo':a,'nombre':labels[a]} for a in labels if motor(actor).base(permiso_baja(tipo,a))]
    return data

@transaction.atomic
def ejecutar_baja(actor,tipo,pk,accion,*,motivo,confirmacion,nombre,acepto):
    from .servicios import auditar,bloqueo_seguridad,motivo_obligatorio,guardar_estado_usuario
    if tipo not in MODELOS or accion not in ('desactivar','eliminar','restaurar','fisica'):raise ValidationError('Operación no disponible.')
    if tipo=='productos' and accion not in ('eliminar','fisica'):raise ValidationError('Operación no disponible para productos.')
    producto=Producto.objects.filter(pk=pk).first() if tipo=='productos' else None
    if tipo!='productos' or producto is not None:autorizar_baja(actor,tipo,accion,producto)
    simple=accion in ("desactivar","restaurar")
    motivo=(motivo.strip() or ("Desactivación confirmada" if accion=="desactivar" else "Restauración confirmada")) if simple else motivo_obligatorio(motivo)
    if simple:motivo=motivo_obligatorio(motivo)
    try:token=signing.loads(confirmacion,salt='baja-administrativa',max_age=600)
    except signing.BadSignature:raise ValidationError('La confirmación caducó. Abre de nuevo la operación.')
    if token['actor']!=actor.pk or token['tipo']!=tipo or token['pk']!=pk:raise PermissionDenied('La confirmación no corresponde a esta operación.')
    if tipo=='productos' and producto is None:exigir(actor,'producto.eliminar',entidad_id=token.get('entidad'))
    bloqueo_seguridad()
    if tipo=='productos' and producto is None:exigir(actor,'producto.eliminar',entidad_id=token.get('entidad'))
    else:autorizar_baja(actor,tipo,accion,producto)
    previous=OperacionAdministrativa.objects.filter(pk=token['nonce'],actor=actor,tipo=tipo,objeto_id=pk,accion=accion).first()
    if previous:return previous.resultado
    if OperacionAdministrativa.objects.filter(pk=token['nonce']).exists():raise ValidationError('La confirmación ya se utilizó para otra operación.')
    obj=MODELOS[tipo].objects.select_for_update().get(pk=pk)
    data=datos_previa(actor,tipo,pk)
    if data['firma_baja']!=token['firma']:raise ValidationError('El registro o sus dependencias cambiaron. Revisa de nuevo la confirmación.')
    if not acepto or (not simple and (accion=='fisica' or data['confirmacion_adicional']) and nombre.strip()!=data['confirmacion_nombre']):raise ValidationError('Confirma la operación y escribe exactamente el nombre o correo indicado.')
    if data['protegido']:raise ValidationError('Esta cuenta o rol es esencial. No se permite esta baja desde el panel.')
    if tipo=='roles':validar_rol(actor,obj,obj.entidad_id)
    if tipo=='usuarios' and UsuarioRol.objects.filter(usuario=obj,rol__codigo='ADMIN_SEGURIDAD',fecha_revocacion__isnull=True).exists() and not administrador_total(actor):raise PermissionDenied('No puedes retirar una cuenta de administración de seguridad.')
    if tipo=='entidades' and not administrador_total(actor):raise PermissionDenied('La baja de organizaciones requiere administración de seguridad.')
    antes=dict(data['estado_baja']);target_name=obj.nombre
    if tipo=='productos':antes['producto']={k:str(getattr(obj,k)) for k in ('nombre','tienda_id','precio','existencias','estado_producto_id','categoria_producto_id','tipo_producto_id')}
    if accion=='fisica':
        if data['dependencias']:raise ValidationError('Hay dependencias. Reasigna los registros o utiliza una baja lógica.')
        collector=Collector(using=obj._state.db)
        try:collector.collect([obj])
        except (ProtectedError,RestrictedError):raise ValidationError('Hay dependencias. Reasigna los registros o utiliza una baja lógica.')
        has_rows=lambda q:q.exists() if hasattr(q,'exists') else bool(q)
        if sum(len(v) for v in collector.data.values())!=1 or any(has_rows(q) for q in collector.fast_deletes) or any(has_rows(q) for batches in collector.field_updates.values() for q in batches):raise ValidationError('El borrado afectaría otros registros. Utiliza una baja lógica.')
        collector.delete()
        nuevo={'eliminado_fisicamente':True}
    else:
        active=accion=='restaurar'
        if tipo=='usuarios':
            if not active:guardar_estado_usuario(actor,obj,{'is_active':False},permiso=f'usuarios.{accion}',registrar=False)
            else:obj.is_active=True;obj.save(update_fields=['is_active'])
        elif tipo=='roles':obj.activo=active;obj.save(update_fields=['activo'])
        elif tipo=='productos':
            from core.models import ValorMaestro
            obj.estado_producto=ValorMaestro.objects.get(tipo__nombre='estado_producto',nombre='Inactivo');obj.save(update_fields=['estado_producto'])
        BajaAdministrativa.objects.update_or_create(tipo=tipo,objeto_id=pk,defaults={'activo':active,'eliminado':accion=='eliminar','autor':actor,'motivo':motivo})
        nuevo={'activo':active,'eliminado':accion=='eliminar'}
    result={'guardado':True,'accion':accion,'tipo':tipo,'id':pk,'estado':nuevo}
    auditar(actor,f'{tipo}.{accion}','producto' if tipo=='productos' else tipo,pk,producto.tienda_id if producto else None,motivo=motivo,elemento_nombre=target_name,anterior=antes,nuevo=nuevo)
    OperacionAdministrativa.objects.create(id=token['nonce'],actor=actor,tipo=tipo,objeto_id=pk,accion=accion,resultado=result)
    from .autorizacion import invalidar
    invalidar()
    return result

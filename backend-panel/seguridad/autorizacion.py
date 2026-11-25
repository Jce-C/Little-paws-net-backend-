"""Motor único: estado activo > superusuario > denegación > concesiones y contexto."""
from contextvars import ContextVar
from django.utils import timezone
from django.db.models import Q, F
from rest_framework.exceptions import PermissionDenied
from accounts.models import Usuario
from core.models import EntidadMiembro, EntidadMiembroRol, Permiso, RolPermiso, UsuarioRol, Rol
from .models import AsignacionFondo, AsignacionRecurso, ResponsableEntidad, ExcepcionPermiso
from .objetos import contexto
from .politicas import POLITICAS

_cache = ContextVar('lpn_motor_peticion', default=None)

def invalidar():
    if _cache.get() is not None:
        _cache.set({})

class Motor:
    def __init__(self, pk):
        from .models import BajaAdministrativa
        self.bajas_entidad=set(BajaAdministrativa.objects.filter(tipo='entidades',activo=False).values_list('objeto_id',flat=True))
        bajas_rol=set(BajaAdministrativa.objects.filter(tipo='roles',activo=False).values_list('objeto_id',flat=True))
        self.usuario = Usuario.objects.filter(pk=pk).first()
        if self.usuario and BajaAdministrativa.objects.filter(tipo='usuarios',objeto_id=pk,activo=False).exists():self.usuario.is_active=False
        self.permisos = {p.codigo:p for p in Permiso.objects.filter(activo=True,recurso__activo=True).select_related('recurso')}
        self.globales = list(UsuarioRol.objects.filter(usuario_id=pk,fecha_revocacion__isnull=True,rol__activo=True,rol__entidad__isnull=True).values('rol_id','rol__codigo','rol__nombre'))
        self.miembros = dict(EntidadMiembro.objects.filter(usuario_id=pk,fecha_salida__isnull=True).values_list('entidad_id','entidad__nombre'))
        self.globales=[r for r in self.globales if r['rol_id'] not in bajas_rol]
        self.miembros={i:n for i,n in self.miembros.items() if i not in self.bajas_entidad}
        self.internos = list(EntidadMiembroRol.objects.filter(miembro__usuario_id=pk,miembro__fecha_salida__isnull=True,fecha_revocacion__isnull=True,rol__activo=True).filter(Q(rol__entidad__isnull=True)|Q(rol__entidad_id=F('miembro__entidad_id'))).values('rol_id','rol__codigo','rol__nombre','miembro__entidad_id'))
        self.internos=[r for r in self.internos if r['rol_id'] not in bajas_rol and r['miembro__entidad_id'] not in self.bajas_entidad]
        self.principales = set(ResponsableEntidad.objects.filter(principal__usuario_id=pk,principal__fecha_salida__isnull=True).values_list('entidad_id',flat=True))
        self.principales-=self.bajas_entidad
        principal = Rol.objects.filter(codigo='RESPONSABLE_PRINCIPAL',activo=True).values('pk','nombre').first()
        if principal:
            asignados_principal={r['miembro__entidad_id'] for r in self.internos if r['rol_id']==principal['pk']}
            self.internos.extend({'rol_id':principal['pk'],'rol__codigo':'RESPONSABLE_PRINCIPAL','rol__nombre':principal['nombre'],'miembro__entidad_id':e} for e in self.principales-asignados_principal)
        ids={x['rol_id'] for x in self.globales+self.internos}
        self.concesiones={i:set() for i in ids}
        for rol,codigo in RolPermiso.objects.filter(rol_id__in=ids).values_list('rol_id','permiso__codigo'):
            self.concesiones[rol].add(codigo)
        self.excepciones=list(ExcepcionPermiso.objects.filter(usuario_id=pk).filter(Q(expira__isnull=True)|Q(expira__gt=timezone.now())).values('permiso__codigo','efecto','contexto_id','motivo','expira'))

    def excepcion(self,codigo,entidad_id=None):
        rows=[e for e in self.excepciones if e['permiso__codigo']==codigo and e['contexto_id']==(entidad_id or 0)]
        return rows[0]['efecto'] if rows else None

    def base(self,codigo,entidad_id=None):
        if entidad_id in self.bajas_entidad and POLITICAS.get(codigo,('','','GLOBAL'))[2]!='GLOBAL':return False
        if not self.usuario or not self.usuario.is_active or codigo not in POLITICAS:
            return False
        if self.usuario.is_superuser:
            return True
        p=self.permisos.get(codigo)
        if not p or (p.recurso.codigo,p.accion,p.alcance)!=POLITICAS[codigo]:
            return False
        global_=p.alcance=='GLOBAL' or p.recurso.codigo in ('verificacion','reclamacion')
        if not global_ and entidad_id not in self.miembros:
            return False
        efecto=self.excepcion(codigo,None if global_ else entidad_id)
        if efecto:
            return efecto=='PERMITIR'
        roles=self.globales + (self.internos if global_ else [r for r in self.internos if r['miembro__entidad_id']==entidad_id])
        return any(codigo in self.concesiones[r['rol_id']] for r in roles)

def motor(usuario):
    pk=getattr(usuario,'pk',usuario)
    cache=_cache.get()
    if cache is None:
        return Motor(pk)
    if pk not in cache:
        cache[pk]=Motor(pk)
    return cache[pk]

def usuario_activo(usuario):
    u=motor(usuario).usuario
    return bool(u and u.is_active)

def es_superusuario(usuario):
    u=motor(usuario).usuario
    return bool(u and u.is_active and u.is_superuser)

def principal_de(usuario,entidad_id):
    m=motor(usuario)
    return bool(m.usuario and m.usuario.is_active and entidad_id in m.principales)

def permiso_vigente(codigo):
    if codigo not in POLITICAS:
        return None
    recurso,accion,alcance=POLITICAS[codigo]
    return Permiso.objects.filter(codigo=codigo,activo=True,recurso__activo=True,recurso__codigo=recurso,accion=accion,alcance=alcance).first()

def tiene_base(usuario,codigo,*,entidad_id=None):
    return motor(usuario).base(codigo,entidad_id)

def puede(usuario, codigo, *, entidad_id=None, objeto_id=None):
    m = motor(usuario)
    if entidad_id in m.bajas_entidad and POLITICAS.get(codigo,('','','GLOBAL'))[2]!='GLOBAL':return False
    if not m.usuario or not m.usuario.is_active:
        return False
    if m.usuario.is_superuser and codigo in POLITICAS:
        return True
    permiso = m.permisos.get(codigo)
    if permiso is None:
        return False
    global_ = permiso.alcance == 'GLOBAL' or permiso.recurso.codigo in ('verificacion','reclamacion')
    contexto_id = entidad_id
    if contexto_id is None and objeto_id is not None and not global_ and permiso.alcance == 'ASIGNADO' and codigo!='adopcion.seguimiento':
        from rest_framework.exceptions import APIException
        try:
            contexto_id = contexto(permiso.recurso.codigo,objeto_id).entidad_id
        except APIException:
            return False
    if m.excepcion(codigo,None if global_ else contexto_id)=='DENEGAR':
        return False
    if codigo == 'adopcion.seguimiento':
        if not objeto_id:return False
        asignacion=AsignacionRecurso.objects.filter(recurso__codigo='adopcion',objeto_id=objeto_id,usuario_id=getattr(usuario,'pk',usuario),fecha_revocacion__isnull=True).first()
        if not asignacion or (entidad_id is not None and entidad_id!=asignacion.entidad_id):return False
        from adoption.models import SolicitudAdopcion
        return tiene_base(usuario,codigo,entidad_id=asignacion.entidad_id) and SolicitudAdopcion.objects.filter(pk=objeto_id,estado_adopcion__nombre='Aprobada').exists()
    if permiso.alcance == Permiso.Alcance.ASIGNADO:
        if objeto_id is None:
            return False
        if permiso.recurso.codigo == "reclamacion":
            from .models import ReclamacionMascota
            return tiene_base(usuario, codigo) and ReclamacionMascota.objects.filter(
                pk=objeto_id, revisor_id=getattr(usuario, "pk", usuario)).exclude(
                reclamante_id=getattr(usuario, "pk", usuario)).exclude(
                mascota__dueno_id=getattr(usuario, "pk", usuario)).exists()
        from rest_framework.exceptions import APIException
        try:
            ctx = contexto(permiso.recurso.codigo, objeto_id)
        except APIException:
            return False
        if ctx.entidad_id is None or (entidad_id is not None and ctx.entidad_id != entidad_id):
            return False
        if not tiene_base(usuario, codigo, entidad_id=ctx.entidad_id):
            return False
        pk = getattr(usuario, "pk", usuario)
        if permiso.recurso.codigo == "fondo":
            return AsignacionFondo.objects.filter(fondo_id=objeto_id, fondo__entidad_id=ctx.entidad_id,
                usuario_id=pk, fecha_revocacion__isnull=True).exists()
        return AsignacionRecurso.objects.filter(recurso=permiso.recurso, objeto_id=objeto_id,
            entidad_id=ctx.entidad_id, usuario_id=pk, fecha_revocacion__isnull=True).exists()
    if permiso.alcance == Permiso.Alcance.AUTORIZADO:
        if codigo == "cuenta.preparar":
            from .models import DelegacionCuenta
            pk = getattr(usuario, "pk", usuario)
            return tiene_base(usuario,codigo,entidad_id=entidad_id) and entidad_id is not None and not principal_de(pk, entidad_id) and DelegacionCuenta.objects.filter(
                entidad_id=entidad_id, miembro__usuario_id=pk,
                miembro__fecha_salida__isnull=True, revocada__isnull=True).exists()
        if objeto_id is None or not usuario_activo(usuario):
            return False
        from core.models import Veterinario
        from animals.models import AutorizacionExpediente
        pk = getattr(usuario, "pk", usuario)
        vet = Veterinario.objects.filter(usuario_profesional_id=pk,
            entidad__estado_verificacion__tipo__nombre="estado_verificacion",
            entidad__estado_verificacion__nombre="Verificada").first()
        if vet is None or not tiene_base(pk, codigo, entidad_id=vet.entidad_id):
            return False
        return AutorizacionExpediente.objects.filter(mascota_id=objeto_id, veterinario=vet,
            fecha_revocacion__isnull=True, fecha_expiracion__gt=timezone.now()).exists()
    if permiso.alcance == Permiso.Alcance.PROPIO:
        # No conceder alcances propios genéricos sin resolver la titularidad real.
        return False
    return tiene_base(usuario, codigo, entidad_id=entidad_id)


def exigir(usuario, codigo, **context):
    if not puede(usuario, codigo, **context):
        raise PermissionDenied("No tienes permiso para esta operación en ese ámbito")

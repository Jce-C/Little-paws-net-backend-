"""Administración en pantalla: mismo motor y servicios que la API."""
import hashlib
import json
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods
from rest_framework.exceptions import APIException, ValidationError, PermissionDenied
from accounts.models import Usuario
from core.models import Rol, Recurso, Permiso, RolPermiso, UsuarioRol, EntidadMiembro, EntidadMiembroRol
from seguridad.autorizacion import exigir, tiene_base, motor
from seguridad.models import ExcepcionPermiso, PreferenciaUsuario
from seguridad.presentacion import presentacion
from seguridad.servicios import asignar_global, asignar_entidad, auditar
from seguridad.serializers import RolSerializer, RecursoSerializer
from .views import protegido
from seguridad.i18n import texto_error
from django.utils.translation import gettext as _t


def firma(rol):
    ids=sorted(RolPermiso.objects.filter(rol=rol).values_list('permiso_id',flat=True))
    return hashlib.sha256(str(ids).encode()).hexdigest()


from seguridad.asignaciones import firma_persona

@protegido
@require_http_methods(['GET','POST'])
def seguridad(request):
    tab=request.GET.get('tab','permisos')
    if tab not in ('roles','recursos','permisos','usuarios','excepciones'):
        tab='permisos'
    permiso={'roles':'roles.ver','recursos':'recursos.ver','permisos':'roles.ver','usuarios':'roles.asignar','excepciones':'roles.asignar'}[tab]
    if tab=='permisos' and tiene_base(request.user,'permisos.ver'):
        pass
    else:
        exigir(request.user,permiso)
    error=''
    status=200
    if request.method=='POST':
        try:
            with transaction.atomic():
                guardar(request,tab)
            messages.success(request,_t('Cambios guardados y enviados a las sesiones abiertas.'))
            if tab in ('roles','recursos'):return redirect(reverse('panel:seguridad')+'?tab='+tab)
            return redirect(request.get_full_path())
        except APIException as exc:
            from seguridad.auditoria_contexto import registrar_fallo
            registrar_fallo(request,exc.status_code,'administracion.'+tab)
            if isinstance(exc,PermissionDenied):raise
            error=texto_error(exc.detail)
        except Recurso.DoesNotExist:
            from seguridad.auditoria_contexto import registrar_fallo
            registrar_fallo(request,404,'administracion.recursos')
            error=_t('El recurso ya no está disponible. Actualiza la lista e inténtalo de nuevo.')
            status=404
        except (ValueError, Rol.DoesNotExist, Usuario.DoesNotExist, Permiso.DoesNotExist, EntidadMiembro.DoesNotExist):
            error='Selecciona registros válidos y revisa los datos del formulario.'
    roles=list((Rol.objects.all() if tab in ('roles','usuarios','excepciones') else Rol.objects.filter(activo=True)).select_related('entidad').order_by('-activo','nombre'))
    recursos=list(Recurso.objects.order_by('nombre'))
    from seguridad.politicas import POLITICAS
    permisos=list(Permiso.objects.filter(activo=True,recurso__activo=True,codigo__in=POLITICAS).select_related('recurso').order_by('recurso__nombre','accion'))
    usuarios=[]
    if tab in ('usuarios','excepciones'):
        q=request.GET.get('q','')[:100]
        from django.db.models import Q
        filtro=Q(nombre__icontains=q)|Q(email__icontains=q)
        if q.isdigit():filtro|=Q(pk=int(q))
        usuarios=list(Usuario.objects.filter(filtro).order_by('nombre')[:10]) if len(q)>=2 or q.isdigit() else []
    rol=next((r for r in roles if str(r.pk)==request.GET.get('rol')),roles[0] if roles else None)
    usuario=next((u for u in usuarios if str(u.pk)==request.GET.get('usuario')),None)
    if request.GET.get('rol') and not any(str(r.pk)==request.GET['rol'] for r in roles):
        raise Http404('Rol no disponible')
    if request.GET.get('usuario'):
        if not request.GET['usuario'].isdigit():raise Http404('Persona no disponible')
        usuario=Usuario.objects.filter(pk=int(request.GET['usuario'])).first()
        if usuario is None:raise Http404('Persona no disponible')
        if not any(u.pk==usuario.pk for u in usuarios):usuarios.insert(0,usuario)
    from core.models import EntidadVerificable
    from seguridad.administracion_segura import administrador_total
    ma=motor(request.user)
    disponibles=EntidadVerificable.objects.exclude(pk__in=ma.bajas_entidad).order_by('nombre')
    if not administrador_total(request.user):disponibles=disponibles.filter(pk__in=[pk for pk in ma.miembros if ma.base('miembros.roles',pk) or ma.base('miembros.gestionar',pk)])
    contextos=list(disponibles)
    miembros=list(EntidadMiembro.objects.filter(usuario=usuario,fecha_salida__isnull=True,entidad__in=contextos).select_related('entidad')) if usuario else []
    entidad=next((e.pk for e in contextos if str(e.pk)==request.GET.get('entidad')),None)
    if request.GET.get('entidad') and entidad is None:raise PermissionDenied('Contexto no disponible para tu cuenta.')
    asignados=set(RolPermiso.objects.filter(rol=rol).values_list('permiso_id',flat=True)) if rol else set()
    excepciones={e.permiso_id:e for e in ExcepcionPermiso.objects.filter(usuario=usuario,contexto_id=entidad or 0)} if usuario else {}
    filas=[]
    for recurso in recursos:
        celdas=[]
        for p in [p for p in permisos if p.recurso_id==recurso.pk]:
            ex=excepciones.get(p.pk)
            info=presentacion(p)
            global_=p.alcance=='GLOBAL' or p.recurso.codigo in ('verificacion','reclamacion')
            celdas.append({'permiso':p,**info,'seleccionado':p.pk in asignados,'bloqueado':bool(entidad) if global_ else not bool(entidad),'efecto':ex.efecto if ex and (not ex.expira or ex.expira>timezone.now()) else 'HEREDAR'})
        if not celdas:
            continue
        fila={'recurso':recurso,'asignado':any(c['seleccionado'] for c in celdas),'otras':[],'consulta':None,'crear':None,'editar':None,'eliminar':None}
        for c in celdas:
            clave={'ver':'consulta','crear':'crear','editar':'editar','eliminar':'eliminar'}.get(c['permiso'].accion)
            if clave:
                fila[clave]=c
            else:
                fila['otras'].append(c)
        filas.append(fila)
    globales=set(UsuarioRol.objects.filter(usuario=usuario,fecha_revocacion__isnull=True).values_list('rol_id',flat=True)) if usuario else set()
    internos=set(EntidadMiembroRol.objects.filter(miembro__usuario=usuario,miembro__entidad_id=entidad,miembro__fecha_salida__isnull=True,fecha_revocacion__isnull=True).values_list('rol_id',flat=True)) if entidad else set()
    from seguridad.models import BajaAdministrativa
    bajas_roles=set(BajaAdministrativa.objects.filter(tipo='roles',activo=False).values_list('objeto_id',flat=True))
    cargos=[]
    for r in roles:
        seleccionado=r.pk in (internos if entidad else globales)
        motivo=''
        if r.pk in bajas_roles:motivo=_t('Restaura el rol archivado antes de asignarlo.')
        elif not r.activo and not tiene_base(request.user,'roles.restaurar'):motivo=_t('Rol inactivo: actívalo desde Roles para asignarlo.')
        elif r.entidad_id and r.entidad_id!=entidad:motivo=_t('Pertenece a otra organización.')
        if not motivo and not administrador_total(request.user):
            from seguridad.administracion_segura import validar_rol
            try:validar_rol(request.user,r,entidad)
            except (PermissionDenied,ValidationError):motivo=_t('Tu autorización no permite modificar este rol.')
        destino=''
        if r.entidad_id and r.entidad_id!=entidad:
            candidato=next((e for e in contextos if r.entidad_id==e.pk),None)
            if candidato:destino=reverse('panel:seguridad')+f'?tab=usuarios&usuario={usuario.pk}&entidad={candidato.pk}' if usuario else ''
        mismo_contexto=r.entidad_id in (None,entidad)
        cargos.append({'rol':r,'seleccionado':seleccionado,'bloqueado':bool(motivo),'motivo':motivo,'destino':destino,'conservar':seleccionado and bool(motivo) and mismo_contexto and r.activo})
    cargos.sort(key=lambda c:(c['bloqueado'],not c['seleccionado'],c['rol'].nombre.casefold()))
    contexto={**request.panel,'tab':tab,'roles_catalogo':roles,'recursos_catalogo':recursos,'rol_elegido':rol,'usuario_elegido':usuario,'usuarios_catalogo':usuarios,'miembros_usuario':miembros,'contextos_roles':contextos,'requiere_membresia':bool(entidad and not any(m.entidad_id==entidad for m in miembros)),'entidad_elegida':entidad,'filas_matriz':filas,'tiene_eliminar':any(f['eliminar'] for f in filas),'cargos':cargos,'cantidad_asignables':sum(not c['bloqueado'] for c in cargos),'roles_seleccionados':[c for c in cargos if c['seleccionado']],'firma':firma(rol) if rol else '', 'error_admin':error,'puede_crear':tiene_base(request.user,('roles' if tab=='roles' else 'recursos')+'.crear'),'puede_guardar':tiene_base(request.user,'roles.editar') if tab in ('roles','permisos') else tiene_base(request.user,'recursos.editar') if tab=='recursos' else tiene_base(request.user,'roles.asignar')}
    editar=request.GET.get('editar','')
    if tab in ('roles','recursos') and (editar or request.GET.get('nuevo')):
        exigir(request.user,tab+('.editar' if editar else '.crear'))
    contexto['elemento_editar']=next((x for x in (roles if tab=='roles' else recursos) if str(x.pk)==editar),None)
    contexto['edicion_nombre']=request.POST.get('nombre',getattr(contexto['elemento_editar'],'nombre',''))
    contexto['edicion_descripcion']=request.POST.get('descripcion',getattr(contexto['elemento_editar'],'descripcion',''))
    contexto['actual']=next((m for m in request.panel['modulos'] if m['codigo']==(tab if tab in ('roles','recursos','permisos') else 'roles-usuario' if tab=='usuarios' else 'excepciones')),{'codigo':'seguridad','nombre':'Seguridad y accesos'})
    contexto['puede_desactivar_roles']=tiene_base(request.user,'roles.desactivar')
    contexto['puede_restaurar_roles']=tiene_base(request.user,'roles.restaurar')
    contexto['puede_bajas_roles']=any(tiene_base(request.user,'roles.'+a) for a in ('eliminar','desactivar','restaurar'))
    contexto['puede_acciones']=tiene_base(request.user,'permisos.editar') or tiene_base(request.user,'permisos.crear')
    contexto['permisos_form_catalogo']=[{'permiso':p,**presentacion(p)} for p in permisos]
    elegido_rol=contexto['elemento_editar'] if tab=='roles' else None
    from seguridad.roles_admin import version_rol
    contexto['version_rol']=version_rol(elegido_rol) if elegido_rol else ''
    grupos={}
    for item in contexto['permisos_form_catalogo']:
        grupos.setdefault(item['permiso'].recurso_id,{'nombre':item['permiso'].recurso.nombre,'permisos':[]})['permisos'].append(item)
    contexto['grupos_permisos_rol']=list(grupos.values())
    contexto['permisos_rol_form']={int(x) for x in request.POST.getlist('permisos') if x.isdigit()} if request.method=='POST' else set(RolPermiso.objects.filter(rol=elegido_rol).values_list('permiso_id',flat=True)) if elegido_rol else set()
    from core.models import EntidadVerificable
    from seguridad.administracion_segura import administrador_total
    contexto['organizaciones_roles']=(EntidadVerificable.objects.all() if administrador_total(request.user) or tiene_base(request.user,'entidades.ver') else EntidadVerificable.objects.filter(pk__in=motor(request.user).miembros)).order_by('nombre') if tiene_base(request.user,'roles.crear') or tiene_base(request.user,'roles.editar') else []
    contexto['rol_form_activo']=(request.POST.get('activo')=='1') if request.method=='POST' else (elegido_rol.activo if elegido_rol else True)
    entidad_rol=request.POST.get('entidad_rol','')
    contexto['rol_form_entidad']=int(entidad_rol) if request.method=='POST' and entidad_rol.isdigit() else elegido_rol.entidad_id if elegido_rol else None
    contexto['firma_persona']=firma_persona(usuario,entidad,tab) if usuario and tab in ('usuarios','excepciones') else ''
    return render(request,'seguridad/web/administracion.html',contexto,status=status)


def guardar(request,tab):
    from seguridad.servicios import bloqueo_seguridad
    bloqueo_seguridad()
    d=request.POST
    if tab in ('roles','recursos'):
        codigo='roles' if tab=='roles' else 'recursos'
        crear=d.get('nuevo')=='1'
        exigir(request.user,f'{codigo}.crear' if crear else f'{codigo}.editar')
        modelo=Rol if tab=='roles' else Recurso
        instancia=None if crear else modelo.objects.select_for_update().get(pk=int(d.get('id','')))
        datos={'nombre':d.get('nombre','').strip(),'descripcion':d.get('descripcion','').strip()}
        if crear:
            datos['codigo']=d.get('codigo','').strip()
            if tab=='roles':
                datos.update(ambito=d.get('ambito','GLOBAL'),delegable=d.get('ambito')=='ENTIDAD')
        if tab=='roles':
            datos.update(permisos=[int(x) for x in d.getlist('permisos')],activo=d.get('activo')=='1',entidad=int(d['entidad_rol']) if d.get('entidad_rol') else None)
        anterior={k:getattr(instancia,k,None) for k in datos} if instancia else None
        s=(RolSerializer if tab=='roles' else RecursoSerializer)(instancia,data=datos,partial=not crear)
        s.is_valid(raise_exception=True)
        if tab=='roles':
            from seguridad.roles_admin import guardar_rol
            guardar_rol(request.user,s.validated_data,instancia,version=d.get('version_rol') if instancia else None)
            return
        obj=s.save()
        auditar(request.user,f'{codigo}.crear' if crear else f'{codigo}.editar',codigo,obj.pk,anterior=anterior,nuevo=datos)
    elif tab=='permisos':
        exigir(request.user,'roles.editar')
        rol=Rol.objects.select_for_update().get(pk=int(d['rol']))
        if d.get('firma')!=firma(rol):
            raise ValidationError('Otra persona modificó esta matriz. Recarga para revisar los cambios antes de guardar.')
        ids=[int(x) for x in d.getlist('permisos')]
        from seguridad.serializers import PermisosRolEntrada
        s=PermisosRolEntrada(data={'permisos':ids});s.is_valid(raise_exception=True)
        from seguridad.politicas import POLITICAS
        if Permiso.objects.filter(pk__in=ids).exclude(codigo__in=POLITICAS).exists():
            raise ValidationError('Selecciona únicamente operaciones implementadas del catálogo.')
        from seguridad.roles_admin import guardar_permisos
        guardar_permisos(request.user,rol,ids)
    elif tab=='usuarios':
        from seguridad.asignaciones import guardar_roles
        guardar_roles(request.user,int(d['usuario']),d.getlist('roles'),int(d['entidad']) if d.get('entidad') else None,d.get('firma_persona'),d.get('motivo',''),d.get('incorporar')=='1',d.get('activar_inactivos')=='1')
    else:
        exigir(request.user,'roles.asignar')
        from seguridad.excepciones import guardar as excepcion
        usuario=Usuario.objects.select_for_update().get(pk=int(d['usuario']))
        entidad=int(d['entidad']) if d.get('entidad') else None
        if d.get('firma_persona')!=firma_persona(usuario,entidad,tab):
            raise ValidationError('Las excepciones de esta persona cambiaron. Recarga antes de guardar.')
        expira=parse_datetime(d['expira']) if d.get('expira') else None
        if d.get('expira') and not expira:
            raise ValidationError('La fecha de caducidad no es válida.')
        if expira and timezone.is_naive(expira):
            expira=timezone.make_aware(expira)
        actuales={e.permiso_id:e for e in ExcepcionPermiso.objects.filter(usuario=usuario,contexto_id=entidad or 0)}
        for campo,efecto in d.items():
            if campo.startswith('excepcion_'):
                pk=int(campo.split('_')[-1]);antes=actuales.get(pk)
                if efecto!=(antes.efecto if antes else 'HEREDAR') or (antes and expira is not None and antes.expira!=expira):
                    excepcion(request.user,usuario.pk,pk,efecto,d.get('motivo',''),entidad,expira)

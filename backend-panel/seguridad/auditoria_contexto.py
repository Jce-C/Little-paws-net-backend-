"""Request correlation and bounded audit metadata; never capture payloads or IPs."""
import hashlib,json,uuid,re
from contextvars import ContextVar
from asgiref.sync import iscoroutinefunction
from django.utils.decorators import sync_and_async_middleware

actual=ContextVar('lpn_audit_request',default=None)
SENSITIVE=re.compile(r'password|passwd|secret|token|credential|authorization|cookie|cifrad|numero_cuenta|cuenta_numero|api_key|apikey|(^|_)numero($|_)|(^|_)clave($|_)',re.I)

def seguro(value,depth=0):
    if depth>5:return '[Límite de profundidad]'
    if isinstance(value,dict):return {str(k)[:80]:seguro(v,depth+1) for k,v in list(value.items())[:80] if not SENSITIVE.search(str(k))}
    if isinstance(value,(list,tuple,set)):return [seguro(v,depth+1) for v in list(value)[:250]]
    if isinstance(value,str):return value[:1500]
    if value is None or isinstance(value,(bool,int,float)):return value
    return str(value)[:1500]

@sync_and_async_middleware
def contexto_auditoria(get_response):
    def enter(request):return actual.set({'request':request,'id':str(uuid.uuid4()),'eventos':{},'operacion_panel':None})
    if iscoroutinefunction(get_response):
        async def middleware(request):
            token=enter(request)
            try:
                response=await get_response(request)
                if response.status_code>=400:
                    from asgiref.sync import sync_to_async
                    await sync_to_async(registrar_respuesta,thread_sensitive=True)(request,response)
                return response
            finally:actual.reset(token)
    else:
        def middleware(request):
            token=enter(request)
            try:
                response=get_response(request)
                registrar_respuesta(request,response)
                return response
            finally:actual.reset(token)
    return middleware

def metadatos(actor,accion,recurso,objeto_id,resultado='EXITO'):
    from core.models import UsuarioRol,EntidadMiembroRol
    ctx=actual.get();name=getattr(actor,'nombre','');pk=getattr(actor,'pk',actor)
    roles=[]
    if pk and not name:
        from accounts.models import Usuario
        name=Usuario.objects.filter(pk=pk).values_list('nombre',flat=True).first() or ''
    if pk:
        rows=list(UsuarioRol.objects.filter(usuario_id=pk,fecha_revocacion__isnull=True,rol__activo=True).values_list('rol__codigo','rol__nombre'))
        rows+=list(EntidadMiembroRol.objects.filter(miembro__usuario_id=pk,miembro__fecha_salida__isnull=True,fecha_revocacion__isnull=True,rol__activo=True).values_list('rol__codigo','rol__nombre'))
        from .models import ResponsableEntidad
        if ResponsableEntidad.objects.filter(principal__usuario_id=pk,principal__fecha_salida__isnull=True).exists():rows.append(('RESPONSABLE_PRINCIPAL','Responsable principal'))
        roles=[r[0] for r in rows]
        if getattr(actor,'is_superuser',False):roles.append('SUPERUSUARIO_TECNICO');rows.append(('SUPERUSUARIO_TECNICO','Superusuario técnico'))
    data={'actor_id':pk,'actor_nombre':name,'roles_vigentes':sorted(set(roles))[:100],'roles_nombres':sorted({r[1] for r in rows})[:100] if pk else [],'roles_total':len(set(roles)),'roles_omitidos':max(0,len(set(roles))-100),'resultado':resultado,'recurso':recurso,'objeto_id':objeto_id}
    from .politicas import POLITICAS
    permiso={'rol.permisos':'roles.editar','rol_global.asignar':'roles.asignar','rol_global.revocar':'roles.asignar','usuario.editar':'usuarios.editar','usuario.crear':'usuarios.crear'}.get(accion,accion)
    data['permiso']=permiso if permiso in POLITICAS else ''
    if ctx:
        req=ctx['request'];data['solicitud']=ctx['id'];data['ruta']=getattr(req.resolver_match,'route','[ruta interna]')[:180];data['metodo']=req.method
        if req.session.session_key and pk:
            if not req.session.get('lpn_traza'):req.session['lpn_traza']=str(uuid.uuid4())
            data['sesion']=req.session['lpn_traza']
        if ctx.get('operacion_panel'):data['operacion_panel']=ctx['operacion_panel']
    return data

def huella(accion,recurso,objeto_id,datos):
    return hashlib.sha256(json.dumps([accion,recurso,objeto_id,datos],sort_keys=True,default=str).encode()).hexdigest()

def registrar_fallo(request,status=400,operacion=None,objeto_id=None):
    ctx=actual.get()
    if not getattr(request.user,'is_authenticated',False) or (ctx and ctx.get('fallo_registrado')):return
    from .servicios import auditar
    if ctx:ctx['fallo_registrado']=True
    match=request.resolver_match
    tipo=getattr(match,'kwargs',{}).get('tipo','')
    route=getattr(match,'route','')
    recurso=tipo if tipo in ('usuarios','roles','entidades') else next((r for r in ('usuarios','roles','recursos','permisos','mascotas','adopcion','pedido') if r in route),'seguridad')
    auditar(request.user,'operacion.rechazada' if status in (401,403) else 'operacion.fallida',recurso,objeto_id,
            resultado='RECHAZADA' if status in (401,403) else 'FALLIDA',estado_http=status,operacion=operacion or getattr(request.resolver_match,'url_name',None) or 'operacion')

def registrar_respuesta(request,response):
    if response.status_code>=400 and request.path.startswith(('/panel/','/api/')) and request.path not in ('/panel/estado/','/panel/eventos/'):
        match=request.resolver_match
        params=getattr(match,'kwargs',{})
        objeto=next((int(v) for k,v in params.items() if (k=='pk' or k.endswith('_id')) and str(v).isdigit()),None)
        registrar_fallo(request,response.status_code,objeto_id=objeto)

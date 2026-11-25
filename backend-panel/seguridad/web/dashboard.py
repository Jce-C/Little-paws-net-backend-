import json
import hashlib
from django.db import transaction
from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods,require_POST
from rest_framework.exceptions import ValidationError
from seguridad.autorizacion import exigir,motor
from seguridad.models import ConfiguracionPanel,PreferenciaUsuario,EventoSeguridad
from seguridad.servicios import auditar
from datetime import datetime,time,timedelta
from django.utils import timezone
from .views import protegido
from django.utils.translation import gettext as _t
from seguridad.i18n import texto_error


def indicadores(request):
    from accounts.models import Usuario
    from animals.models import Mascota
    from rescue.models import Reporte
    from adoption.models import SolicitudAdopcion
    m=motor(request.user)
    datos=[]
    if m.base('adopcion.participar') or m.base('mascotas.ver'):
        from adoption.consultas import disponibles_adopcion
        from urllib.parse import urlencode
        datos.append({'nombre':'Mascotas disponibles para adopción','valor':disponibles_adopcion().count(),'url':'/panel/areas/mascotas/?'+urlencode({'estado':'En adopción'}) if any(x['codigo']=='mascotas' for x in request.panel['modulos']) else ''})
    if m.base('reportes.participar'):
        datos.append({'nombre':'Mis reportes','valor':Reporte.objects.filter(usuario_reportante=request.user).count()})
    if m.base('adopcion.participar'):
        datos.append({'nombre':'Mis solicitudes de adopción','valor':SolicitudAdopcion.objects.filter(usuario_adoptante=request.user).count()})
    entidad=request.panel['entidad_id']
    from .negocio import filas
    for area,capacidad,etiqueta in [('rescates','caso.ver','Rescates visibles en mi organización'),('adopciones','adopcion.ver','Adopciones disponibles para mi gestión'),('aportes','aporte.ver','Aportes disponibles para mi gestión'),('pedidos','pedido.ver','Pedidos disponibles para mi gestión'),('expedientes','expediente.escribir','Expedientes con acceso disponible')]:
        if m.base(capacidad,entidad):
            datos.append({'nombre':etiqueta,'valor':len(filas(request,area)),'limitado':True})
    if m.base('usuarios.ver'):
        datos.insert(0,{'nombre':'Usuarios registrados','valor':Usuario.objects.count()})
    if m.base('auditoria.ver'):
        inicio=timezone.make_aware(datetime.combine(timezone.localdate(),time.min))
        datos.append({'nombre':'Acciones registradas hoy','valor':EventoSeguridad.objects.filter(fecha__gte=inicio,fecha__lt=inicio+timedelta(days=1)).count()})
    for indicador in datos:
        nombre=indicador['nombre'].casefold()
        indicador['icono']=next((icono for texto,icono in [('usuarios','users'),('mascotas','paw-print'),('reportes','clipboard-check'),('solicitudes','heart-handshake'),('acciones','history'),('rescates','paw-print'),('adopciones','heart-handshake'),('aportes','hand-coins'),('pedidos','shopping-bag'),('expedientes','stethoscope')] if texto in nombre),'chart-no-axes-combined')
    return datos


def inicio(request):
    grupos={}
    for p in request.panel['resumen_permisos']:
        grupos.setdefault(str(p['modulo']),[]).append(p)
    maximo=max([len(v) for v in grupos.values()] or [1])
    grafico=[{'nombre':k,'valor':len(v),'maximo':maximo} for k,v in grupos.items()]
    comparativa=[]
    if motor(request.user).base('mascotas.ver'):
        from animals.models import Mascota
        from django.db.models import Count
        cantidades=dict(Mascota.objects.filter(estado_mascota__nombre__in=['En adopción','Adoptada']).values_list('estado_mascota__nombre').annotate(total=Count('pk')))
        tope=max([cantidades.get(n,0) for n in ('En adopción','Adoptada')]+[1])
        comparativa=[{'nombre':_t(n),'valor':cantidades.get(n,0),'maximo':tope} for n in ('En adopción','Adoptada')]
    actividad=EventoSeguridad.objects.all() if motor(request.user).base('auditoria.ver') else EventoSeguridad.objects.filter(actor=request.user)
    return render(request,'seguridad/web/inicio.html',{**request.panel,'indicadores':indicadores(request),'comparativa_adopcion':comparativa,'grafico_accesos':sorted(grafico,key=lambda x:x['valor'],reverse=True)[:6],'grafico_restante':sorted(grafico,key=lambda x:x['valor'],reverse=True)[6:],'total_capacidades':len(request.panel['resumen_permisos']),'total_areas':len(grupos),'grupos_acceso':grupos.items(),'actividad':[{'descripcion':descripcion_evento(e),'actor':e.actor.nombre if e.actor else _t('Sistema'),'fecha':e.fecha} for e in actividad.select_related('actor')[:6]]})


@protegido
@require_http_methods(['GET','POST'])
def configuracion(request):
    exigir(request.user,'configuracion.ver')
    opciones={'titulo_panel':'Título del panel','subtitulo_panel':'Mensaje del dashboard','titulo_landing':'Título de bienvenida','texto_landing':'Presentación de la aplicación','login_fondo_opacidad':'Intensidad de la imagen (0,35 a 1)','login_fondo_velo':'Velo de legibilidad (0 a 0,45)','login_fondo_posicion':'Encuadre de la imagen','login_fondo_visible':'Mostrar imagen de fondo'}
    from .titulos_navegacion import opciones as opciones_navegacion
    navegacion=opciones_navegacion()
    opciones.update({k:v['nombre'] for k,v in navegacion.items()})
    def version_config():
        datos=dict(ConfiguracionPanel.objects.values_list('clave','valor'))
        return hashlib.sha256(json.dumps(datos,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    error=''
    if request.method=='POST':
        try:
            exigir(request.user,'configuracion.editar')
            with transaction.atomic():
                from seguridad.servicios import bloqueo_seguridad
                bloqueo_seguridad()
                if request.POST.get('version_config') and request.POST['version_config']!=version_config():
                    raise ValidationError('Otra persona cambió la configuración. Recarga para revisar sus cambios antes de guardar.')
                for clave in opciones:
                    if clave not in request.POST:
                        continue
                    nuevo=request.POST[clave].strip()
                    if clave in ('login_fondo_opacidad','login_fondo_velo'):
                        try:numero=float(nuevo.replace(',','.'))
                        except ValueError:raise ValidationError('Indica un número válido para la intensidad o el velo.')
                        minimo,maximo=(0.35,1) if clave=='login_fondo_opacidad' else (0,0.45)
                        if not minimo<=numero<=maximo:raise ValidationError(f'El valor debe estar entre {minimo} y {maximo}.')
                        nuevo=str(numero)
                    if clave=='login_fondo_posicion' and nuevo not in ('center center','center top','center bottom'):raise ValidationError('Selecciona un encuadre válido.')
                    if clave=='login_fondo_visible' and nuevo not in ('si','no'):raise ValidationError('Selecciona si se muestra el fondo.')
                    if clave in navegacion:
                        if len(nuevo)>80:
                            raise ValidationError('Los títulos del menú admiten un máximo de 80 caracteres.')
                        obj=ConfiguracionPanel.objects.select_for_update().filter(clave=clave).first()
                        anterior=obj.valor if obj else ''
                        if anterior!=nuevo:
                            objeto_id=obj.pk if obj else None
                            if nuevo:
                                obj,_=ConfiguracionPanel.objects.update_or_create(clave=clave,defaults={'valor':nuevo})
                                objeto_id=obj.pk
                            elif obj:
                                obj.delete()
                            auditar(request.user,'configuracion.editar','configuracion',objeto_id,motivo=request.POST.get('motivo','Actualización de títulos de navegación'),elemento_nombre=navegacion[clave]['grupo']+' · '+navegacion[clave]['nombre'],anterior={clave:anterior},nuevo={clave:nuevo})
                        continue
                    if not nuevo or len(nuevo)>500:
                        raise ValidationError('Completa los textos, con un máximo de 500 caracteres.')
                    obj,_=ConfiguracionPanel.objects.select_for_update().get_or_create(clave=clave,defaults={'valor':nuevo})
                    anterior=obj.valor
                    if anterior!=nuevo:
                        obj.valor=nuevo;obj.save(update_fields=['valor'])
                        auditar(request.user,'configuracion.editar','configuracion',obj.pk,motivo=request.POST.get('motivo','Actualización de textos'),anterior={clave:anterior},nuevo={clave:nuevo})
            messages.success(request,_t('Configuración actualizada en las sesiones abiertas.'))
            return redirect('panel:configuracion')
        except ValidationError as exc:
            from seguridad.auditoria_contexto import registrar_fallo
            registrar_fallo(request,400,'configuracion.editar')
            error=texto_error(exc.detail)
    return render(request,'seguridad/web/configuracion.html',{**request.panel,'actual':next((m for m in request.panel['modulos'] if m['codigo']=='configuracion'),None),'version_config':request.POST.get('version_config',version_config()),'opciones_config':[{'clave':k,'nombre':v,'valor':request.POST.get(k,request.panel['config_panel'].get(k,{'login_fondo_opacidad':'1','login_fondo_velo':'0.12','login_fondo_posicion':'center center','login_fondo_visible':'si'}.get(k,''))),'grupo':navegacion[k]['grupo'] if k in navegacion else 'Acceso' if k.startswith('login_') else 'Textos','navegacion':k in navegacion,'defecto':navegacion[k]['defecto'] if k in navegacion else ''} for k,v in opciones.items()],'error_admin':error,'editable':motor(request.user).base('configuracion.editar')})


@protegido
@require_POST
def perfil(request):
    from .contexto import PERFILES_VISUALES
    permitidos={x[0] for x in PERFILES_VISUALES.values()}|{'ciudadano','preparador_cuentas'}
    valor=request.POST.get('perfil_visual')
    if valor not in permitidos:
        return JsonResponse({'detalle':'Selecciona un perfil visual válido'},status=400)
    obj,_=PreferenciaUsuario.objects.get_or_create(usuario=request.user)
    anterior=obj.perfil_visual;obj.perfil_visual=valor;obj.save(update_fields=['perfil_visual'])
    auditar(request.user,'perfil.color','usuarios',request.user.pk,anterior=anterior,nuevo=valor)
    if 'application/json' not in request.headers.get('Accept',''):
        from django.utils.http import url_has_allowed_host_and_scheme
        destino=request.POST.get('next','/panel/')
        if not destino.startswith('/panel/') or not url_has_allowed_host_and_scheme(destino,{request.get_host()},require_https=request.is_secure()):destino='/panel/'
        return redirect(destino)
    return JsonResponse({'guardado':True,'perfil':valor})


def descripcion_evento(evento):
    from .presentacion_eventos import descripcion_reciente
    reciente = descripcion_reciente(evento)
    if reciente is not None:
        return reciente
    nombres={'rol.permisos':'Cambió los permisos de un rol','permiso.excepcion':'Cambió una excepción individual','usuario.editar':'Actualizó una cuenta','usuario.crear':'Creó una cuenta','usuarios.crear':'Creó una cuenta','recursos.editar':'Actualizó un recurso del menú','roles.editar':'Actualizó un rol','roles.crear':'Creó un rol','recursos.crear':'Creó un recurso','rol_entidad.asignar':'Asignó un cargo de organización','rol_entidad.revocar':'Retiró un cargo de organización','rol_global.asignar':'Asignó un rol de plataforma','rol_global.revocar':'Retiró un rol de plataforma','configuracion.editar':'Actualizó la configuración de plataforma','sesion.web_iniciar':'Inició sesión','sesion.web_cerrar':'Cerró sesión','sesion.cambiar_clave':'Cambió su contraseña','registro.consultar':'Consultó un registro privado'}
    nombres.update({'productos.eliminar':'Archivó un producto del catálogo','productos.fisica':'Eliminó definitivamente un producto','caso.registrar_mascota':'Vinculó una mascota rescatada con su caso y custodia','mascotas.publicar_adopcion':'Actualizó la disponibilidad para adopción','catalogos.inicializar':'Preparó los catálogos iniciales de producción','reporte.crear':'Registró un reporte de situación','catalogos.crear':'Añadió una referencia al catálogo','catalogos.editar':'Actualizó una referencia del catálogo','caso.cobertura':'Actualizó la cobertura por ciudad','mascota.declarar':'Registró una mascota'})
    for recurso in ('usuarios','roles','entidades'):
        for accion,label in [('desactivar','Desactivó un registro'),('restaurar','Restauró un registro'),('eliminar','Archivó un registro'),('fisica','Eliminó definitivamente un registro')]:nombres[recurso+'.'+accion]=label
    if evento.accion=='rol.permisos' and evento.datos.get('elemento_nombre'):return _t('Cambió los permisos del rol %(rol)s') % {'rol':evento.datos['elemento_nombre']}
    if evento.accion=='rol_global.asignar' and evento.datos.get('rol_nombre'):return _t('Asignó el rol %(rol)s al usuario #%(id)s') % {'rol':evento.datos['rol_nombre'],'id':evento.objeto_id}
    if evento.accion=='sesion.web_rechazada':return _t('Inicio de sesión rechazado')
    if evento.accion=='registro.consultar':
        from seguridad.politicas import RECURSOS
        return _t('Consultó %(recurso)s #%(id)s') % {'recurso':_t(RECURSOS.get(evento.recurso,evento.recurso)),'id':evento.objeto_id or '—'}
    if evento.accion=='negocio.operacion' and evento.motivo:return evento.motivo
    return nombres.get(evento.accion,_t('Actividad registrada: %(codigo)s') % {'codigo':evento.accion})


@protegido
@require_http_methods(['GET'])
def auditoria(request):
    exigir(request.user,'auditoria.ver')
    from django.core.paginator import Paginator
    from django.db.models import Q,Case,When,Value,CharField
    from django import forms
    from accounts.models import Usuario
    from seguridad.presentacion import presentacion
    from core.models import Permiso,Recurso
    textos={p.codigo:str(presentacion(p)['nombre']) for p in Permiso.objects.select_related('recurso')}
    recursos=dict(Recurso.objects.values_list('codigo','nombre'))
    clases={'acceso':'Acceso','consulta':'Consulta','seguridad':'Seguridad','creacion':'Creación','edicion':'Edición','operacion':'Operación'}
    categoria=Case(When(accion__startswith='sesion.',then=Value('acceso')),When(accion='registro.consultar',then=Value('consulta')),When(Q(accion__startswith='rol')|Q(accion__startswith='permiso')|Q(accion__startswith='principal')|Q(accion__startswith='miembro')|Q(accion__startswith='django_admin'),then=Value('seguridad')),When(Q(accion__contains='.crear')|Q(accion__contains='.registrar'),then=Value('creacion')),When(Q(accion__contains='.editar')|Q(accion__contains='.actualizar'),then=Value('edicion')),default=Value('operacion'),output_field=CharField())
    qs=EventoSeguridad.objects.select_related('actor','entidad').annotate(categoria=categoria).order_by('-pk')
    q=request.GET.get('q','')[:100];error=''
    if q:qs=qs.filter(Q(accion__icontains=q)|Q(actor__nombre__icontains=q)|Q(motivo__icontains=q)|Q(recurso__icontains=q))
    actor=request.GET.get('actor','');tipo=request.GET.get('tipo','')
    if actor:
        if not actor.isdigit():error='Selecciona una persona válida.';qs=qs.none()
        else:qs=qs.filter(actor_id=int(actor))
    if tipo in clases:qs=qs.filter(categoria=tipo)
    fechas={}
    for key,lookup in [('desde','fecha__date__gte'),('hasta','fecha__date__lte')]:
        valor=request.GET.get(key,'')
        if valor:
            try:
                fechas[key]=forms.DateField().clean(valor)
                inicio=timezone.make_aware(datetime.combine(fechas[key],time.min))
                qs=qs.filter(**({'fecha__gte':inicio} if key=='desde' else {'fecha__lt':inicio+timedelta(days=1)}))
            except forms.ValidationError:error='Indica las fechas en un formato válido.';qs=qs.none()
    if len(fechas)==2 and fechas['desde']>fechas['hasta']:error='La fecha inicial debe ser anterior o igual a la final.';qs=qs.none()
    recurso_filtro=request.GET.get('recurso','')
    if recurso_filtro:qs=qs.filter(recurso=recurso_filtro)
    resultado=request.GET.get('resultado','')
    if resultado in ('EXITO','FALLIDA','RECHAZADA'):qs=qs.filter(datos___contexto__resultado=resultado)
    if request.GET.get('exportar')=='csv':
        from .exportar_auditoria import exportar
        return exportar(request,qs)
    total=qs.count()
    page=Paginator(qs,25).get_page(request.GET.get('pagina'))
    from .titulos_navegacion import opciones as opciones_navegacion
    etiquetas_nav={k:str(_t(v['nombre'])) for k,v in opciones_navegacion().items()}
    def legible(valor):
        if isinstance(valor,list):return '\n'.join(textos.get(str(x),_t(str(x))) for x in valor) or _t('Sin valores')
        if isinstance(valor,dict):return '\n'.join(f'{etiquetas_nav.get(k,_t(k.replace("_"," ").capitalize()))}: {_t("Usar nombre habitual") if k in etiquetas_nav and v=="" else legible(v)}' for k,v in valor.items() if not any(s in k.lower() for s in ['password','token','cifrado','numero_cuenta']))
        if isinstance(valor,bool):return _t('Sí') if valor else _t('No')
        return textos.get(str(valor),_t(str(valor)) if valor is not None else _t('Sin valor'))
    eventos=[{'obj':e,'descripcion':descripcion_evento(e),'categoria':clases[e.categoria],'recurso_nombre':recursos.get(e.recurso,e.recurso or 'Plataforma'),'anterior':legible(e.datos.get('anterior',e.datos.get('anteriores',_t('Este evento no registró un valor anterior.')))),'nuevo':legible(e.datos.get('nuevo',e.datos.get('nuevos',_t('Este evento no registró un valor nuevo.'))))} for e in page]
    for e in eventos:
        meta=e['obj'].datos.get('_contexto',{})
        e.update(actor_snapshot=meta.get('actor_nombre') or getattr(e['obj'].actor,'nombre',_t('Acceso sin autenticar') if e['obj'].accion=='sesion.web_rechazada' else _t('Reportante con clave privada') if e['obj'].accion=='reporte.gestion_anonima' else _t('Sistema')),roles_snapshot=meta.get('roles_nombres',meta.get('roles_vigentes',[])),resultado=meta.get('resultado',_t('No registrado')),referencia_sesion=meta.get('sesion',''),referencia_solicitud=meta.get('solicitud',''),permiso_operacion=meta.get('permiso',''),elemento_nombre=e['obj'].datos.get('elemento_nombre',''))
    from .presentacion_eventos import informacion_evento
    for evento in eventos:
        evento['informacion_adicional'] = informacion_evento(evento['obj'])
    for e in eventos:e['resultado_texto']={'EXITO':_t('Exitosa'),'FALLIDA':_t('Fallida'),'RECHAZADA':_t('Rechazada')}.get(e['resultado'],e['resultado'])
    grupos_auditoria=[]
    agrupar=request.GET.get('agrupar','')
    if agrupar in ('usuario','sesion'):
        from collections import OrderedDict
        groups=OrderedDict()
        for e in eventos:
            key=str(e['obj'].actor_id) if agrupar=='usuario' else e['referencia_sesion'] or 'evento-'+str(e['obj'].pk)
            groups.setdefault(key,[]).append(e)
        eventos=[]
        for key,items in groups.items():
            for e in items:e.update(grupo=key,grupo_cantidad=len(items))
            grupos_auditoria.append({'nombre':items[0]['actor_snapshot'],'sesion':items[0]['referencia_sesion'] if agrupar=='sesion' else '', 'cantidad':len(items),'desde':min(x['obj'].fecha for x in items),'hasta':max(x['obj'].fecha for x in items),'eventos':items,'exitos':sum(x['resultado']=='EXITO' for x in items),'rechazos':sum(x['resultado']=='RECHAZADA' for x in items)})
            eventos.extend(items)
    parametros=request.GET.copy();parametros.pop('pagina',None)
    contexto_extra={'grupos_auditoria':grupos_auditoria,'filtros_agrupacion':[(k,request.GET[k]) for k in ('q','actor','tipo','desde','hasta','recurso','resultado') if request.GET.get(k)],'filtros_activos':sum(bool(request.GET.get(k)) for k in ['q','actor','tipo','desde','hasta','recurso','resultado']),'agrupar':agrupar,'recursos_auditoria':recursos.items(),'puede_exportar':motor(request.user).base('auditoria.exportar')}

    actores=Usuario.objects.filter(pk__in=EventoSeguridad.objects.exclude(actor=None).values('actor_id')).order_by('nombre').values('pk','nombre')
    return render(request,'seguridad/web/auditoria.html',{**request.panel,**contexto_extra,'actual':next((m for m in request.panel['modulos'] if m['codigo']=='auditoria'),None),'eventos':eventos,'paginacion':page,'actores_auditoria':actores,'tipos_evento':clases.items(),'total_eventos':total,'filtros_query':parametros.urlencode(),'error_filtros':error})

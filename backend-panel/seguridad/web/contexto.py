from django.utils.translation import gettext_lazy as _t
"""Navegación derivada de permisos actuales, nunca de una selección del navegador."""
from core.models import EntidadMiembro, UsuarioRol, Rol
from seguridad.autorizacion import tiene_base, puede, principal_de
from seguridad.models import AsignacionRecurso, ResponsableEntidad
MODULOS = [('usuarios', _t('Usuarios'), _t('Seguridad'), 'usuarios.ver', 'GLOBAL', _t('Personas y estado de sus cuentas')), ('roles', _t('Roles y permisos'), _t('Seguridad'), 'roles.ver', 'GLOBAL', _t('Responsabilidades y acciones permitidas')), ('recursos', _t('Recursos'), _t('Seguridad'), 'recursos.ver', 'GLOBAL', _t('Módulos protegidos de la plataforma')), ('permisos', _t('Permisos'), _t('Seguridad'), 'permisos.ver', 'GLOBAL', _t('Acciones reconocidas y su alcance')), ('auditoria', _t('Auditoría'), _t('Seguridad'), 'auditoria.ver', 'GLOBAL', _t('Registro de acciones administrativas')), ('verificaciones', _t('Verificaciones'), _t('Moderación'), 'verificacion.tomar', 'GLOBAL', _t('Solicitudes disponibles para revisión')), ('reclamaciones', _t('Reclamaciones'), _t('Moderación'), 'reclamacion.tomar', 'GLOBAL', _t('Revisión de titularidad en dos pasos')), ('revision-publicidad', _t('Revisión de anuncios'), _t('Moderación'), 'publicidad.revisar', 'GLOBAL', _t('Contenido pendiente de aprobación')), ('equipo', _t('Equipo y responsables'), _t('Mi organización'), 'miembros.ver', 'ENTIDAD', _t('Integrantes y responsabilidades de tu entidad')), ('cuentas', _t('Cuentas receptoras'), _t('Mi organización'), 'cuenta.aprobar', 'ENTIDAD', _t('Propuestas y aprobación de cambios')), ('rescates', _t('Casos de rescate'), _t('Operación'), 'caso.ver', 'ENTIDAD', _t('Casos de tu fundación')), ('adopciones', _t('Adopciones'), _t('Operación'), 'adopcion.tomar', 'ENTIDAD', _t('Solicitudes pendientes de asignación')), ('aportes', _t('Aportes'), _t('Operación'), 'aporte.tomar', 'ENTIDAD', _t('Revisiones disponibles, sin ejecutar pagos')), ('pedidos', _t('Pedidos'), _t('Operación'), 'pedido.tomar', 'ENTIDAD', _t('Trabajo disponible de tu tienda')), ('catalogo', _t('Catálogo'), _t('Operación'), 'producto.gestionar', 'ENTIDAD', _t('Productos, precios y disponibilidad')), ('fondos', _t('Fondos asignados'), _t('Operación'), 'fondo.ver', 'ENTIDAD', _t('Fondos en los que puedes trabajar')), ('publicidad', _t('Publicidad'), _t('Operación'), 'publicidad.gestionar', 'ENTIDAD', _t('Anuncios y versiones de tu entidad')), ('expedientes', _t('Expedientes autorizados'), _t('Atención veterinaria'), 'expediente.escribir', 'ENTIDAD', _t('Mascotas con autorización vigente'))]
ICONOS = dict(zip((m[0] for m in MODULOS), ('users', 'shield-check', 'boxes', 'key-round', 'history', 'clipboard-check', 'scale', 'megaphone', 'building-2', 'landmark', 'paw-print', 'heart-handshake', 'hand-coins', 'shopping-bag', 'package', 'chart-no-axes-combined', 'megaphone', 'stethoscope')))
PERFILES_VISUALES = {'ADMIN_SEGURIDAD': ('admin_seguridad', _t('Administrador de seguridad')), 'MODERADOR': ('moderador', _t('Moderador de plataforma')), 'RESPONSABLE_PRINCIPAL': ('responsable_principal', _t('Responsable principal')), 'RESPONSABLE_SECUNDARIO': ('responsable_secundario', _t('Responsable secundario')), 'GESTOR_RESCATES': ('gestor_rescates', _t('Gestor de rescates')), 'GESTOR_ADOPCIONES': ('gestor_adopciones', _t('Gestor de adopciones')), 'GESTOR_APORTES': ('gestor_aportes', _t('Gestor de aportes')), 'GESTOR_CATALOGO': ('gestor_catalogo', _t('Gestor de catálogo')), 'GESTOR_PEDIDOS': ('gestor_pedidos', _t('Gestor de pedidos')), 'GESTOR_FONDO': ('gestor_fondo', _t('Gestor de fondo')), 'GESTOR_PUBLICIDAD': ('gestor_publicidad', _t('Gestor de publicidad')), 'VETERINARIO': ('veterinario', _t('Veterinario verificado'))}

def perfil_visual(codigos, preparador=False):
    """Prioridad visual estable para cuentas con varios roles simultáneos."""
    for codigo, perfil in PERFILES_VISUALES.items():
        if codigo in codigos:
            return perfil
    if preparador:
        return ('preparador_cuentas', _t('Preparador delegado de cuentas'))
    return ('', _t('Equipo autorizado'))

def construir(request):
    from seguridad.autorizacion import motor
    from seguridad.models import PreferenciaUsuario, ConfiguracionPanel
    from core.models import Recurso, EntidadVerificable
    from seguridad.presentacion import presentacion
    from .titulos_navegacion import preparar_modulos, textos
    config=dict(ConfiguracionPanel.objects.values_list("clave","valor"))
    m=motor(request.user)
    organizaciones=[{'id':pk,'nombre':nombre,'roles':[r['rol__codigo'] for r in m.internos if r['miembro__entidad_id']==pk]} for pk,nombre in m.miembros.items()]
    if m.usuario and m.usuario.is_superuser:
        organizaciones=[{'id':e.pk,'nombre':e.nombre,'roles':[]} for e in EntidadVerificable.objects.exclude(pk__in=m.bajas_entidad).order_by('nombre')]
    seleccion=next((e for e in organizaciones if e['id']==request.session.get('lpn_entidad')),organizaciones[0] if organizaciones else None)
    entidad_id=seleccion['id'] if seleccion else None
    nombres={r.codigo:r for r in Recurso.objects.all()}
    modulos=[]
    for codigo,nombre,grupo,permiso,ambito,descripcion in MODULOS:
        recurso=permiso.split('.')[0]
        candidatos=[permiso]
        if codigo=='permisos':candidatos.append('roles.ver')
        if codigo in ('adopciones','aportes','pedidos'):
            candidatos += [recurso+'.ver',recurso+'.resolver' if codigo=='adopciones' else recurso+'.gestionar']
        autorizado=any(m.base(p,entidad_id) for p in candidatos)
        if codigo=='cuentas':
            autorizado=autorizado or puede(request.user,'cuenta.preparar',entidad_id=entidad_id)
        if autorizado:
            r=nombres.get(recurso)
            modulos.append({'codigo':codigo,'nombre':r.nombre if r else nombre,'grupo':grupo,'descripcion':r.descripcion if r and r.descripcion else descripcion,'icono':ICONOS[codigo],'recurso':recurso})
    extras=[('catalogos','catalogos.ver','Administración','boxes'),('organizaciones','entidades.ver','Organizaciones y equipos','building-2'),('mascotas','mascotas.ver','Mascotas y rescates','paw-print'),('reportes','reportes.ver','Mascotas y rescates','clipboard-check')]
    for codigo,permiso,grupo,icono in extras:
        if m.base(permiso) or (codigo=='organizaciones' and m.base('miembros.ver',entidad_id)):
            rec=nombres.get(permiso.split('.')[0])
            modulos.append({'codigo':codigo,'nombre':rec.nombre if rec else codigo.title(),'grupo':grupo,'descripcion':rec.descripcion if rec and rec.descripcion else 'Listado, formularios y trazabilidad del proceso.','icono':icono,'recurso':permiso.split('.')[0]})
    # Participación ciudadana conserva los controles propios de cada proceso.
    for codigo,recurso,label,grupo,icono in [('mascotas','mascotas','Mascotas','Mi participación','paw-print'),('adopciones','adopcion','Mis adopciones','Mi participación','heart-handshake'),('reportes','reportes','Mis reportes','Mi participación','clipboard-check'),('aportes','aporte','Mis aportes','Mi participación','hand-coins'),('catalogo','producto','Catálogo','Mi participación','package'),('pedidos','pedido','Mis pedidos','Mi participación','shopping-bag'),('fondos','fondo','Fondos externos','Mi participación','chart-no-axes-combined'),('reclamaciones','reclamacion','Mis reclamaciones','Mi participación','scale')]:
        participacion={'mascotas':'mascotas.participar','adopciones':'adopcion.participar','reportes':'reportes.participar','aportes':'aporte.participar','catalogo':'producto.consultar','pedidos':'pedido.participar','reclamaciones':'reclamacion.presentar','fondos':'fondo.participar'}[codigo]
        if m.base(participacion) and not any(x['codigo']==codigo for x in modulos):
            rec=nombres.get(recurso)
            modulos.append({'codigo':codigo,'nombre':rec.nombre if rec else label,'grupo':grupo,'descripcion':'Tus procesos y las acciones que están autorizadas para tu cuenta.','icono':icono,'recurso':recurso})
    if m.base('configuracion.ver'):
        modulos.append({'codigo':'configuracion','nombre':nombres.get('configuracion').nombre if nombres.get('configuracion') else 'Configuración','grupo':'Administración','descripcion':'Títulos y textos de la plataforma','icono':'sliders-horizontal','recurso':'configuracion'})
    globales=[str(_t(r['rol__nombre'])) for r in m.globales]
    codigos=[r['rol__codigo'] for r in m.globales]+[r['rol__codigo'] for r in m.internos]
    tema,etiqueta=perfil_visual(codigos)
    tema=tema or 'ciudadano'
    pref,_=PreferenciaUsuario.objects.get_or_create(usuario=request.user,defaults={'perfil_visual':'admin_seguridad' if m.usuario.is_superuser else tema})
    resumen=[]
    for codigo,p in m.permisos.items():
        global_=p.alcance=='GLOBAL' or p.recurso.codigo in ('verificacion','reclamacion')
        if m.base(codigo,entidad_id):
            elegibles=m.globales+(m.internos if global_ else [r for r in m.internos if r['miembro__entidad_id']==entidad_id])
            origen=['Superusuario técnico'] if m.usuario.is_superuser else [str(_t(r['rol__nombre']))+' · '+(m.miembros.get(r.get('miembro__entidad_id'),str(_t('Plataforma')))) for r in elegibles if codigo in m.concesiones[r['rol_id']]]
            ex=m.excepcion(codigo,None if global_ else entidad_id)
            if ex=='PERMITIR' and not m.usuario.is_superuser:origen=['Excepción individual: permitir']
            resumen.append({'codigo':codigo,**presentacion(p),'origen':origen})
    if m.base('roles.asignar'):
        modulos.extend([{'codigo':'roles-usuario','nombre':'Roles por persona','grupo':_t('Seguridad'),'descripcion':'Asignación de varios roles por persona','icono':'users','recurso':'roles'},{'codigo':'excepciones','nombre':'Excepciones individuales','grupo':_t('Seguridad'),'descripcion':'Permitir o denegar capacidades a una persona','icono':'key-round','recurso':'roles'}])
    orden_grupos={}
    for item in modulos:orden_grupos.setdefault(str(item['grupo']),len(orden_grupos))
    modulos.sort(key=lambda item:orden_grupos[str(item['grupo'])])
    from django.urls import reverse
    from .negocio import AREAS
    for modulo in modulos:
        for label in ('nombre','grupo','descripcion'):modulo[label]=str(_t(modulo[label]))
        codigo=modulo['codigo']
        if codigo in ('roles-usuario','excepciones'):
            modulo['url']=reverse('panel:seguridad')+'?tab='+('usuarios' if codigo=='roles-usuario' else 'excepciones')
            continue
        modulo['url']=(reverse('panel:seguridad')+'?tab='+codigo) if codigo in ('roles','recursos','permisos') else reverse('panel:configuracion') if codigo=='configuracion' else reverse('panel:catalogos') if codigo=='catalogos' else reverse('panel:auditoria') if codigo=='auditoria' else reverse('panel:area',args=[codigo]) if codigo in AREAS else reverse('panel:area',args=['organizaciones']) if codigo in ('equipo','cuentas') else reverse('panel:usuarios') if codigo=='usuarios' else reverse('panel:modulo',args=[codigo])
    preparar_modulos(modulos,config)
    roles_visibles=list(dict.fromkeys(globales+[str(_t(r['rol__nombre'])) for r in m.internos if r['miembro__entidad_id']==entidad_id]))
    from .navegacion import organizar
    return {**organizar(modulos,config),'titulos_nav':textos(config),'organizaciones':organizaciones,'seleccion':seleccion,'entidad_id':entidad_id,'modulos':modulos,'modulos_nav':[m for m in modulos if m['codigo']!='configuracion'],'globales':globales,'puede_panel':bool(m.usuario and m.usuario.is_active),'perfil_visual':pref.perfil_visual,'rol_visible':'Superusuario técnico' if m.usuario.is_superuser else ' · '.join(roles_visibles) or etiqueta,'resumen_permisos':resumen,'perfiles_colores':[(v[0],v[1]) for v in PERFILES_VISUALES.values()]+[('ciudadano','Ciudadano')],'config_panel':config}

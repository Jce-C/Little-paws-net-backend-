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
    usuario = request.user
    organizaciones = []
    for miembro in EntidadMiembro.objects.filter(usuario=usuario, fecha_salida__isnull=True).select_related('entidad'):
        codigos = list(miembro.entidadmiembrorol_set.filter(fecha_revocacion__isnull=True, rol__activo=True, rol__ambito='ENTIDAD').exclude(rol__codigo='RESPONSABLE_PRINCIPAL').values_list('rol__codigo', flat=True))
        if principal_de(usuario, miembro.entidad_id):
            codigos.append('RESPONSABLE_PRINCIPAL')
        if codigos or puede(usuario, 'cuenta.preparar', entidad_id=miembro.entidad_id):
            organizaciones.append({'id': miembro.entidad_id, 'nombre': miembro.entidad.nombre, 'roles': codigos})
    seleccion = next((e for e in organizaciones if e['id'] == request.session.get('lpn_entidad')), organizaciones[0] if organizaciones else None)
    entidad_id = seleccion['id'] if seleccion else None
    modulos = []
    for codigo, nombre, grupo, permiso, ambito, descripcion in MODULOS:
        autorizado = tiene_base(usuario, permiso, entidad_id=entidad_id if ambito == 'ENTIDAD' else None)
        if codigo == 'cuentas':
            autorizado = autorizado or puede(usuario, 'cuenta.preparar', entidad_id=entidad_id)
        if autorizado:
            modulos.append({'codigo': codigo, 'nombre': nombre, 'grupo': grupo, 'descripcion': descripcion, 'icono': ICONOS[codigo]})
    roles_globales = list(UsuarioRol.objects.filter(usuario=usuario, fecha_revocacion__isnull=True, rol__activo=True, rol__ambito='GLOBAL').exclude(rol__codigo='CIUDADANO').values_list('rol__codigo', 'rol__nombre'))
    globales = [nombre for _, nombre in roles_globales]
    tema, etiqueta = perfil_visual([codigo for codigo, _ in roles_globales] + (seleccion['roles'] if seleccion else []), preparador=any((m['codigo'] == 'cuentas' for m in modulos)))
    return {'organizaciones': organizaciones, 'seleccion': seleccion, 'entidad_id': entidad_id, 'modulos': modulos, 'globales': globales, 'puede_panel': bool(modulos), 'perfil_visual': tema, 'rol_visible': etiqueta}

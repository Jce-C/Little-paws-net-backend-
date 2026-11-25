"""Editable presentation labels; never identifiers, routes or authorization rules."""
from django.utils.translation import gettext as _

GRUPOS = {
    'seguridad': 'Seguridad', 'administracion': 'Administración',
    'organizaciones': 'Organizaciones y equipos', 'mascotas': 'Mascotas y rescates',
    'participacion': 'Mi participación', 'moderacion': 'Moderación',
    'mi_organizacion': 'Mi organización', 'operacion': 'Operación',
    'veterinaria': 'Atención veterinaria',
}
MODULOS = {
    'usuarios':'Usuarios', 'roles':'Roles', 'recursos':'Recursos', 'permisos':'Permisos',
    'auditoria':'Auditoría de seguridad', 'verificaciones':'Verificaciones',
    'reclamaciones':'Reclamaciones', 'revision-publicidad':'Revisión de anuncios',
    'equipo':'Equipo y responsables', 'cuentas':'Cuentas receptoras',
    'rescates':'Casos de rescate', 'adopciones':'Adopciones', 'aportes':'Aportes',
    'pedidos':'Pedidos', 'catalogo':'Catálogo', 'fondos':'Fondos',
    'publicidad':'Publicidad', 'expedientes':'Expedientes autorizados',
    'catalogos':'Catálogos del sistema', 'organizaciones':'Entidades',
    'mascotas':'Mascotas', 'reportes':'Reportes de rescate',
    'configuracion':'Configuración', 'roles-usuario':'Roles por persona',
    'excepciones':'Excepciones individuales',
}
TEXTOS = {
    'nav_submarca':'PANEL DE GESTIÓN', 'nav_inicio':'Mi espacio', 'nav_accesos':'Roles y recursos',
    'nav_espacio':'ESPACIO DE TRABAJO', 'nav_autorizados':'MÓDULOS AUTORIZADOS',
    'nav_estado':'Accesos actualizados',
    'nav_pie':'Cada persona, con lo que necesita para cuidar.',
}

def clave_modulo(codigo):
    return 'nav_mod_' + codigo.replace('-', '_')

def opciones():
    return {
        **{k:{'nombre':v,'grupo':'Navegación: encabezados','defecto':v} for k,v in TEXTOS.items()},
        **{'nav_grupo_'+k:{'nombre':v,'grupo':'Navegación: secciones','defecto':v} for k,v in GRUPOS.items()},
        **{clave_modulo(k):{'nombre':v,'grupo':'Navegación: opciones','defecto':v} for k,v in MODULOS.items()},
    }

def titulo(config, clave, defecto):
    return config.get(clave, '').strip() or str(_(defecto))

def codigo_grupo(nombre):
    return next((k for k,v in GRUPOS.items() if str(nombre) in (v,str(_(v)))), None)

def preparar_modulos(modulos, config):
    for modulo in modulos:
        modulo['grupo_codigo'] = codigo_grupo(modulo['grupo'])
        modulo['nombre'] = titulo(config, clave_modulo(modulo['codigo']), modulo['nombre'])
        modulo['titulo'] = str(_('Permisos por rol')) if modulo['codigo']=='permisos' and not config.get(clave_modulo('permisos'),'').strip() and modulo['nombre']==str(_('Permisos')) else modulo['nombre']

def textos(config):
    return {k:titulo(config,k,v) for k,v in TEXTOS.items()}

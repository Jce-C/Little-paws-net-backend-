"""Correspondencia explícita: no se introduce un segundo catálogo user_permissions."""
from .autorizacion import es_superusuario, puede
from .politicas import POLITICAS

MODELOS = {'usuario': 'usuarios', 'rol': 'roles', 'recurso': 'recursos', 'permiso': 'permisos',
    'eventoseguridad': 'auditoria', 'entidadverificable': 'entidades'}
ACCIONES = {'view': 'ver', 'add': 'crear', 'change': 'editar', 'delete': 'eliminar'}


def permitido(usuario, permiso, obj=None):
    if es_superusuario(usuario):
        return True
    if permiso in POLITICAS:
        return puede(usuario, permiso)
    if '.' not in permiso or '_' not in permiso.split('.')[-1]:
        return False
    accion, modelo = permiso.split('.')[-1].split('_', 1)
    codigo = f'{MODELOS.get(modelo, modelo)}.{ACCIONES.get(accion, accion)}'
    return codigo in POLITICAS and puede(usuario, codigo)


def modulo_permitido(usuario, app):
    if es_superusuario(usuario):
        return True
    recursos = {'accounts': ['usuarios'], 'core': ['roles', 'recursos', 'permisos', 'entidades'], 'seguridad': ['auditoria']}.get(app, [])
    return any(puede(usuario, f'{r}.ver') for r in recursos)

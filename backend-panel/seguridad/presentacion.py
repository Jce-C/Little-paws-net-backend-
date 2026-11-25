"""Etiquetas humanas; los códigos estables siguen siendo la identidad del permiso."""
from django.utils.translation import gettext_lazy as _
from .politicas import RECURSOS

ACCIONES = {
    'ver': _('Consultar'), 'crear': _('Crear'), 'editar': _('Editar'), 'eliminar':_('Eliminar'),'desactivar':_('Desactivar'),'restaurar':_('Restaurar'),'exportar':_('Exportar'),
}
NOMBRES = {
    'comunidad.participar': _('Publicar, comentar y reaccionar en la comunidad'),
    'comunidad.moderar': _('Moderar publicaciones públicas'),
    'ayudas.participar': _('Ofrecer tiempo o ayuda en especie'),
    'ayudas.gestionar': _('Gestionar convocatorias y ofrecimientos de mi organización'),
    'producto.eliminar':_('Eliminar productos del catálogo'),
    'caso.registrar_mascota':_('Registrar una mascota rescatada'),
    'caso.cobertura':_('Configurar cobertura por ciudad'),
    'mascotas.publicar_adopcion':_('Actualizar disponibilidad para adopción'),
    'mascotas.participar': _('Consultar y registrar mis mascotas'),
    'reportes.participar': _('Crear y gestionar mis reportes'),
    'adopcion.participar': _('Consultar y gestionar mis solicitudes de adopción'),
    'aporte.participar': _('Registrar y consultar mis aportes'),
    'pedido.participar': _('Crear y consultar mis pedidos'),
    'fondo.participar': _('Participar en fondos y registrar mis compromisos'),
    'producto.consultar': _('Consultar el catálogo público'),
    'reclamacion.presentar': _('Presentar y consultar mis reclamaciones'),
    'adopcion.seguimiento': _('Registrar seguimiento de una adopción aprobada'),
    'roles.asignar': _('Asignar o retirar roles de plataforma'),
    'entidades.ver': _('Consultar organizaciones'),
    'principal.designar': _('Designar al responsable principal'),
    'auditoria.ver': _('Consultar el historial de seguridad'),
    'miembros.ver': _('Consultar integrantes del equipo'),
    'miembros.gestionar': _('Incorporar o retirar integrantes'),
    'miembros.roles': _('Asignar o retirar cargos del equipo'),
    'principal.transferir': _('Transferir la responsabilidad principal'),
    'caso.ver': _('Consultar casos de rescate'),
    'caso.aceptar': _('Aceptar un reporte de rescate'),
    'caso.cambiar_estado': _('Actualizar el estado de un rescate'),
    'producto.gestionar': _('Administrar productos y existencias'),
    'publicidad.gestionar': _('Crear y actualizar anuncios'),
    'fondo.solicitar': _('Solicitar un fondo externo'),
    'fondo.asignar': _('Asignar gestores a un fondo'),
    'expediente.autorizar': _('Autorizar atención veterinaria'),
    'adopcion.tomar': _('Tomar una solicitud de adopción'),
    'adopcion.ver': _('Consultar una adopción asignada'),
    'adopcion.resolver': _('Aprobar o rechazar una adopción'),
    'aporte.tomar': _('Tomar una revisión de aporte'),
    'aporte.ver': _('Consultar un aporte asignado'),
    'aporte.confirmar': _('Confirmar la recepción de un aporte'),
    'pedido.tomar': _('Tomar un pedido pendiente'),
    'pedido.ver': _('Consultar un pedido asignado'),
    'pedido.gestionar': _('Actualizar un pedido asignado'),
    'fondo.ver': _('Consultar un fondo asignado'),
    'fondo.reportar_distribucion': _('Registrar la distribución de un fondo'),
    'verificacion.tomar': _('Tomar una verificación pendiente'),
    'verificacion.ver': _('Consultar una verificación asignada'),
    'entidad.validar': _('Resolver la verificación de una organización'),
    'cuenta.delegar': _('Delegar la preparación de cuentas receptoras'),
    'cuenta.aprobar': _('Aprobar una cuenta receptora preparada'),
    'cuenta.preparar': _('Preparar una propuesta de cuenta receptora'),
    'reclamacion.tomar': _('Tomar una reclamación de titularidad'),
    'reclamacion.resolver': _('Resolver una reclamación de titularidad'),
    'reclamacion.ejecutar': _('Ejecutar un cambio de titularidad aprobado'),
    'publicidad.revisar': _('Revisar anuncios para su publicación'),
    'reporte.moderar': _('Moderar reportes publicados'),
    'expediente.escribir': _('Registrar atención en un expediente autorizado'),
}


def presentacion(permiso):
    recurso = permiso.recurso.codigo
    modulo = _(RECURSOS.get(recurso, permiso.recurso.nombre))
    nombre = NOMBRES.get(permiso.codigo)
    if nombre is None:
        nombre = '%s %s' % (ACCIONES.get(permiso.accion, permiso.accion), str(modulo).lower())
    alcance, ayuda = {
        'GLOBAL': (_('Plataforma'), _('Se aplica a la plataforma; los datos privados conservan sus controles.')),
        'ENTIDAD': (_('Su organización'), _('Solo dentro de la organización en la que tiene un cargo vigente.')),
        'ASIGNADO': (_('Registros asignados'), _('Requiere además que el registro esté asignado a esta persona.')),
        'AUTORIZADO': (_('Autorización específica'), _('Requiere una autorización o delegación vigente para ese registro.')),
    }.get(permiso.alcance, (_('Acceso propio'), _('Solo sobre registros propios autorizados.')))
    if permiso.accion in ('participar','presentar'):
        alcance,ayuda=_('Participación propia'),_('Solo tus procesos propios; no concede acceso a los de otras personas.')
    return {'nombre': nombre, 'modulo': modulo, 'alcance_nombre': alcance, 'ayuda': ayuda}

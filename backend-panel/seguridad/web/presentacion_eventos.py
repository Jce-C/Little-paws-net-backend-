"""Readable audit presentation without changing records or exposing payloads."""
from django.utils.translation import gettext as _


def descripcion_reciente(evento):
    codigo = evento.accion
    if codigo == 'reporte.gestion_anonima':
        nuevo = evento.datos.get('nuevo', {})
        return _('Cerró un reporte con su clave privada') if isinstance(nuevo, dict) and nuevo.get('estado') == 'Cerrado' else _('Actualizó un reporte con su clave privada')
    if codigo == 'ayudas.programa_publico':
        before, after = evento.datos.get('anterior', {}), evento.datos.get('nuevo', {})
        before = before if isinstance(before, dict) else {}
        after = after if isinstance(after, dict) else {}
        if after.get('publicada') is True:
            return _('Actualizó las actividades y canales públicos de ayuda') if before.get('publicada') is True else _('Publicó las actividades y canales de ayuda')
        return _('Retiró la convocatoria pública de ayuda') if before.get('publicada') is True else _('Guardó un borrador de actividades y canales')
    if codigo == 'mascotas.presentacion_publica':
        before, after = evento.datos.get('anterior', {}), evento.datos.get('nuevo', {})
        before = before if isinstance(before, dict) else {}
        after = after if isinstance(after, dict) else {}
        if after.get('publicada') is True:
            return _('Actualizó la descripción y cuidados públicos de la mascota') if before.get('publicada') is True else _('Publicó la descripción y cuidados de la mascota')
        return _('Retiró la presentación pública de la mascota') if before.get('publicada') is True else _('Guardó un borrador de presentación de la mascota')
    if codigo == 'entidad.perfil_publico':
        before, after = evento.datos.get('anterior', {}), evento.datos.get('nuevo', {})
        before = before if isinstance(before, dict) else {}
        after = after if isinstance(after, dict) else {}
        if after.get('publicada') is True:
            return _('Actualizó la ficha pública de la organización') if before.get('publicada') is True else _('Publicó la ficha de la organización')
        return _('Retiró la ficha pública de la organización') if before.get('publicada') is True else _('Guardó un borrador de la ficha pública')
    if codigo == 'perfil.foto_publicar':
        return _('Reemplazó su foto pública de perfil') if evento.datos.get('reemplazo') is True else _('Publicó su foto de perfil en Comunidad')
    if codigo == 'perfil.foto_retirar':
        return _('Retiró su foto pública de perfil')
    if codigo == 'entidad.logo_publicar':
        return _('Reemplazó el logo público de la organización') if evento.datos.get('reemplazo') is True else _('Publicó el logo de la organización')
    if codigo == 'entidad.logo_retirar':
        return _('Retiró el logo público de la organización')
    if codigo == 'producto.foto_publicar':
        return _('Reemplazó la fotografía pública del producto') if evento.datos.get('reemplazo') is True else _('Publicó una fotografía del producto')
    if codigo == 'producto.foto_retirar':
        return _('Retiró la fotografía pública del producto')
    if codigo in ('mascotas.foto_publicar', 'mascota.foto_publicar'):
        if evento.datos.get('reemplazo') is True:
            return _('Reemplazó la fotografía pública para adopción')
        return _('Publicó una fotografía para adopción')
    if codigo in ('mascotas.foto_retirar', 'mascota.foto_retirar'):
        return _('Retiró la fotografía pública de adopción')
    if codigo == 'perfil.actualizar':
        return _('Actualizó sus datos de contacto')
    if codigo == 'adopcion.participar' and evento.datos.get('operacion') == 'solicitar-adopcion':
        return _('Envió una solicitud de adopción')
    if codigo == 'operacion.fallida':
        return _('La operación devolvió un error')
    if codigo == 'operacion.rechazada':
        return _('La operación fue rechazada')
    return None


def informacion_evento(evento):
    """Allow-listed facts only: no field values, payloads or image storage keys."""
    codigo = evento.accion
    if codigo == 'reporte.gestion_anonima':
        nuevo = evento.datos.get('nuevo', {})
        campos = nuevo.get('campos_modificados', []) if isinstance(nuevo, dict) else []
        nombres = [nombre for campo, nombre in [('descripcion', _('Descripción')), ('contacto_reportante', _('Contacto privado')), ('estado_reporte', _('Estado'))] if campo in campos]
        return _('Campos actualizados: %(campos)s. No se conservan aquí la clave ni el contenido privado.') % {'campos': ', '.join(nombres)}
    if codigo in ('mascotas.foto_publicar', 'mascota.foto_publicar', 'producto.foto_publicar', 'entidad.logo_publicar', 'perfil.foto_publicar'):
        imagen = evento.datos.get('nuevo')
        if isinstance(imagen, dict) and all(type(imagen.get(k)) is int and imagen[k] > 0 for k in ('ancho', 'alto', 'bytes')):
            return _('Imagen: %(ancho)s × %(alto)s px · %(bytes)s bytes.') % {k: imagen[k] for k in ('ancho', 'alto', 'bytes')}
    if codigo == 'perfil.actualizar':
        campos = evento.datos.get('campos')
        if isinstance(campos, list):
            nombres = [nombre for campo, nombre in [('nombre', _('Nombre')), ('telefono', _('Teléfono'))] if campo in campos]
            if nombres:
                return _('Campos actualizados: %(campos)s.') % {'campos': ', '.join(nombres)}
    if codigo in ('operacion.fallida', 'operacion.rechazada'):
        estado = evento.datos.get('estado_http')
        if type(estado) is int and 400 <= estado <= 599:
            return _('Respuesta HTTP: %(estado)s.') % {'estado': estado}
    return ''

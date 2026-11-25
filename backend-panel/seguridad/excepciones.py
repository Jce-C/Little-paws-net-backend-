from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from core.models import Permiso, EntidadMiembro
from accounts.models import Usuario
from .models import ExcepcionPermiso
from .autorizacion import exigir
from .servicios import auditar, motivo_obligatorio


@transaction.atomic
def guardar(actor, usuario_id, permiso_id, efecto, motivo, entidad_id=None, expira=None):
    exigir(actor, 'roles.asignar')
    motivo = motivo_obligatorio(motivo)
    usuario = Usuario.objects.select_for_update().get(pk=usuario_id, is_active=True)
    permiso = Permiso.objects.select_related('recurso').get(pk=permiso_id, activo=True, recurso__activo=True)
    from .politicas import POLITICAS
    if POLITICAS.get(permiso.codigo)!=(permiso.recurso.codigo,permiso.accion,permiso.alcance):
        raise ValidationError('El permiso no corresponde a una operación implementada.')
    if efecto not in ('HEREDAR', 'PERMITIR', 'DENEGAR'):
        raise ValidationError('Selecciona Heredar, Permitir o Denegar')
    if expira is not None and expira <= timezone.now():
        raise ValidationError('La caducidad debe estar en el futuro')
    if efecto=='PERMITIR':
        from .administracion_segura import delegables
        delegables(actor,[permiso.codigo],entidad_id)
    global_ = permiso.alcance == 'GLOBAL' or permiso.recurso.codigo in ('verificacion', 'reclamacion')
    if global_ and entidad_id is not None:
        raise ValidationError('Este permiso de plataforma no recibe una organización')
    if not global_ and entidad_id is None:
        raise ValidationError('Selecciona la organización de esta excepción')
    if entidad_id and not EntidadMiembro.objects.filter(usuario=usuario, entidad_id=entidad_id, fecha_salida__isnull=True).exists():
        raise ValidationError('La persona debe pertenecer a la organización')
    contexto = entidad_id or 0
    filtro = dict(usuario=usuario, permiso=permiso, contexto_id=contexto)
    anterior = ExcepcionPermiso.objects.filter(**filtro).values('efecto', 'motivo', 'expira').first()
    if anterior and anterior['expira']:
        anterior['expira'] = anterior['expira'].isoformat()
    if efecto == 'HEREDAR':
        ExcepcionPermiso.objects.filter(**filtro).delete()
    else:
        ExcepcionPermiso.objects.update_or_create(**filtro, defaults=dict(entidad_id=entidad_id,
            efecto=efecto, motivo=motivo, autor=actor, expira=expira))
    from .servicios import limpiar_asignaciones
    limpiar_asignaciones(usuario.pk)
    auditar(actor, 'permiso.excepcion', 'usuarios', usuario.pk, entidad_id, motivo,
            permiso=permiso.codigo, anterior=anterior or {'efecto': 'HEREDAR'},
            nuevo={'efecto': efecto, 'expira': expira.isoformat() if expira else None})

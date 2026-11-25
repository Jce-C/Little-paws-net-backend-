from django.db.models import F
from django.db.models.signals import post_save, post_delete
from .autorizacion import invalidar
from .models import RevisionPanel


def cambio(sender, **kwargs):
    if kwargs.get('raw') or kwargs.get('update_fields')==frozenset({'last_login'}):
        return
    if sender._meta.label_lower=='seguridad.eventoseguridad':
        accion=kwargs['instance'].accion
        # Consultar no cambia datos: evita que dos detalles abiertos se recarguen entre sí.
        if accion=='registro.consultar' or accion.startswith('sesion.'):
            return
    invalidar()
    if not RevisionPanel.objects.filter(pk=1).update(version=F('version') + 1):
        RevisionPanel.objects.get_or_create(pk=1, defaults={'version':1})


def conectar():
    from django.apps import apps
    nombres = [('accounts', 'Usuario'), ('core', 'Rol'), ('core', 'Recurso'), ('core', 'Permiso'),
        ('core', 'RolPermiso'), ('core', 'UsuarioRol'), ('core', 'EntidadMiembro'), ('core', 'EntidadMiembroRol'),
        ('seguridad', 'ResponsableEntidad'), ('seguridad', 'ExcepcionPermiso'), ('seguridad', 'ConfiguracionPanel'),
        ('seguridad', 'PreferenciaUsuario'), ('seguridad', 'EventoSeguridad')]
    for app, nombre in nombres:
        modelo = apps.get_model(app, nombre)
        for signal in (post_save, post_delete):
            signal.connect(cambio, sender=modelo, dispatch_uid=f'lpn_revision_{signal}_{app}_{nombre}')

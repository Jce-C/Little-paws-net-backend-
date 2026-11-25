from django.db import migrations


def iniciar(apps, schema_editor):
    db = schema_editor.connection.alias
    apps.get_model('seguridad', 'RevisionPanel').objects.using(db).get_or_create(pk=1)
    recurso, _ = apps.get_model('core', 'Recurso').objects.using(db).get_or_create(codigo='configuracion', defaults={'nombre':'Configuración de la plataforma'})
    admin = apps.get_model('core','Rol').objects.using(db).filter(codigo='ADMIN_SEGURIDAD').first()
    for accion in ('ver','editar'):
        permiso, _ = apps.get_model('core','Permiso').objects.using(db).get_or_create(codigo=f'configuracion.{accion}', defaults={'recurso':recurso,'accion':accion,'alcance':'GLOBAL','descripcion':'Configuración de títulos y textos del panel'})
        if admin:
            apps.get_model('core','RolPermiso').objects.using(db).get_or_create(rol=admin,permiso=permiso)
    Config = apps.get_model('seguridad','ConfiguracionPanel')
    for clave,valor in {'titulo_panel':'Panel de gestión','subtitulo_panel':'Cada cuidado empieza con un buen equipo.','titulo_landing':'Pequeñas patas. Grandes historias.','texto_landing':'Conectamos a las personas que hacen posible una segunda oportunidad.'}.items():
        Config.objects.using(db).get_or_create(clave=clave,defaults={'valor':valor})


class Migration(migrations.Migration):
    dependencies = [('seguridad', '0008_configuracionpanel_revisionpanel_preferenciausuario_and_more')]
    operations = [migrations.RunPython(iniciar,migrations.RunPython.noop)]

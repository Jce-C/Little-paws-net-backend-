from django.db import migrations

def cargar(apps,schema_editor):
    Permiso=apps.get_model('core','Permiso');Recurso=apps.get_model('core','Recurso');Rol=apps.get_model('core','Rol');RolPermiso=apps.get_model('core','RolPermiso')
    admin=Rol.objects.filter(codigo='ADMIN_SEGURIDAD').first()
    for codigo in [f'{r}.{a}' for r in ('usuarios','roles','entidades') for a in ('eliminar','desactivar','restaurar')]+['auditoria.exportar']:
        recurso,accion=codigo.split('.')
        rec=Recurso.objects.get(codigo=recurso)
        p,_=Permiso.objects.get_or_create(codigo=codigo,defaults={'recurso':rec,'accion':accion,'alcance':'GLOBAL','descripcion':codigo,'activo':True})
        if admin:RolPermiso.objects.get_or_create(rol=admin,permiso=p)

class Migration(migrations.Migration):
    dependencies=[('seguridad','0015_idempotencia_administrativa')]
    operations=[migrations.RunPython(cargar,migrations.RunPython.noop)]

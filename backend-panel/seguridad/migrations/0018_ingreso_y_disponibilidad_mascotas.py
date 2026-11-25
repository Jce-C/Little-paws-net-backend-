from django.db import migrations

def cargar(apps,schema_editor):
    P=apps.get_model('core','Permiso');R=apps.get_model('core','Recurso');Rol=apps.get_model('core','Rol');RP=apps.get_model('core','RolPermiso')
    for code,recurso,accion,cargo in [('caso.registrar_mascota','caso','registrar_mascota','GESTOR_RESCATES'),('mascotas.publicar_adopcion','mascotas','publicar_adopcion','GESTOR_ADOPCIONES')]:
        p,_=P.objects.get_or_create(codigo=code,defaults={'recurso':R.objects.get(codigo=recurso),'accion':accion,'alcance':'ENTIDAD','activo':True,'descripcion':code})
        for rol in Rol.objects.filter(codigo__in=[cargo,'ADMIN_SEGURIDAD']):RP.objects.get_or_create(rol=rol,permiso=p)

class Migration(migrations.Migration):
    dependencies=[('seguridad','0017_catalogos_y_cobertura')]
    operations=[migrations.RunPython(cargar,migrations.RunPython.noop)]

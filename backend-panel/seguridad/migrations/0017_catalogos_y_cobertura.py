from django.db import migrations

def cargar(apps,schema_editor):
    Recurso=apps.get_model('core','Recurso');Permiso=apps.get_model('core','Permiso');Rol=apps.get_model('core','Rol');RP=apps.get_model('core','RolPermiso')
    rec,_=Recurso.objects.get_or_create(codigo='catalogos',defaults={'nombre':'Catálogos del sistema','descripcion':'Ciudades, especies y razas'})
    admin=Rol.objects.filter(codigo='ADMIN_SEGURIDAD').first()
    for code,accion,alcance,recurso in [('catalogos.'+a,a,'GLOBAL',rec) for a in ('ver','crear','editar')]+[('caso.cobertura','cobertura','ENTIDAD',Recurso.objects.get(codigo='caso'))]:
        p,_=Permiso.objects.get_or_create(codigo=code,defaults={'recurso':recurso,'accion':accion,'alcance':alcance,'activo':True,'descripcion':code})
        if admin:RP.objects.get_or_create(rol=admin,permiso=p)
        if code=='caso.cobertura':
            for rol in Rol.objects.filter(codigo__in=['RESPONSABLE_PRINCIPAL','RESPONSABLE_SECUNDARIO']):RP.objects.get_or_create(rol=rol,permiso=p)

class Migration(migrations.Migration):
    dependencies=[('seguridad','0016_catalogo_fase_dos'),('core','0009_ciudad_activo_ciudad_codigo_divipola'),('animals','0005_especie_activo_raza_activo')]
    operations=[migrations.RunPython(cargar,migrations.RunPython.noop)]

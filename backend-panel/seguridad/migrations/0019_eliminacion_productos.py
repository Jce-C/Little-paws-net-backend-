from django.db import migrations,models

def cargar(apps,schema_editor):
    P=apps.get_model('core','Permiso');R=apps.get_model('core','Recurso');Rol=apps.get_model('core','Rol');RP=apps.get_model('core','RolPermiso')
    p,_=P.objects.get_or_create(codigo='producto.eliminar',defaults={'recurso':R.objects.get(codigo='producto'),'accion':'eliminar','alcance':'ENTIDAD','activo':True,'descripcion':'Eliminar productos del catálogo'})
    for rol in Rol.objects.filter(codigo__in=['GESTOR_CATALOGO','ADMIN_SEGURIDAD']):RP.objects.get_or_create(rol=rol,permiso=p)
class Migration(migrations.Migration):
    dependencies=[('seguridad','0018_ingreso_y_disponibilidad_mascotas')]
    operations=[migrations.AlterField(model_name='bajaadministrativa',name='tipo',field=models.CharField(max_length=16,choices=[('usuarios','Usuarios'),('roles','Roles'),('entidades','Entidades'),('productos','Productos')])),migrations.RunPython(cargar,migrations.RunPython.noop)]

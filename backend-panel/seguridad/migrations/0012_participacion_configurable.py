from django.db import migrations
DATOS={'mascotas.participar': ('mascotas', 'participar'), 'reportes.participar': ('reportes', 'participar'), 'adopcion.participar': ('adopcion', 'participar'), 'aporte.participar': ('aporte', 'participar'), 'pedido.participar': ('pedido', 'participar'), 'fondo.participar': ('fondo', 'participar'), 'producto.consultar': ('producto', 'consultar'), 'reclamacion.presentar': ('reclamacion', 'presentar')}
def cargar(apps,schema_editor):
 db=schema_editor.connection.alias
 for codigo,(recurso,accion) in DATOS.items():
  r,_=apps.get_model('core','Recurso').objects.using(db).get_or_create(codigo=recurso,defaults={'nombre':recurso.title()})
  p,_=apps.get_model('core','Permiso').objects.using(db).get_or_create(codigo=codigo,defaults={'recurso':r,'accion':accion,'alcance':'GLOBAL','descripcion':'Participación con datos propios y recursos públicos'})
  for rol in apps.get_model('core','Rol').objects.using(db).filter(codigo__in=['CIUDADANO','ADMIN_SEGURIDAD']):
   apps.get_model('core','RolPermiso').objects.using(db).get_or_create(rol=rol,permiso=p)
 # La capacidad no permite operar sin delegación vigente ni aprobar la propia propuesta.
 p=apps.get_model('core','Permiso').objects.using(db).get(codigo='cuenta.preparar')
 for rol in apps.get_model('core','Rol').objects.using(db).filter(codigo='CIUDADANO'):
  apps.get_model('core','RolPermiso').objects.using(db).get_or_create(rol=rol,permiso=p)
class Migration(migrations.Migration):
 dependencies=[('seguridad','0011_catalogo_administracion_negocio')]
 operations=[migrations.RunPython(cargar,migrations.RunPython.noop)]

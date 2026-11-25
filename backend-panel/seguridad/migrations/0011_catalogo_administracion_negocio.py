from django.db import migrations

DATOS={
'entidades.crear':('entidades','crear','GLOBAL'),'entidades.editar':('entidades','editar','GLOBAL'),
'mascotas.ver':('mascotas','ver','GLOBAL'),'mascotas.crear':('mascotas','crear','GLOBAL'),'mascotas.editar':('mascotas','editar','GLOBAL'),
'reportes.ver':('reportes','ver','GLOBAL'),'fondo.crear':('fondo','crear','GLOBAL'),'fondo.editar':('fondo','editar','GLOBAL'),
'adopcion.seguimiento':('adopcion','seguimiento','ASIGNADO')}

def cargar(apps,schema_editor):
 db=schema_editor.connection.alias
 Recurso=apps.get_model('core','Recurso');Permiso=apps.get_model('core','Permiso');Rol=apps.get_model('core','Rol');RP=apps.get_model('core','RolPermiso')
 for codigo,(recurso,accion,alcance) in DATOS.items():
  r,_=Recurso.objects.using(db).get_or_create(codigo=recurso,defaults={'nombre':{'mascotas':'Mascotas','reportes':'Reportes de rescate'}.get(recurso,recurso.title())})
  p,_=Permiso.objects.using(db).get_or_create(codigo=codigo,defaults={'recurso':r,'accion':accion,'alcance':alcance,'descripcion':codigo})
  rol=Rol.objects.using(db).filter(codigo='GESTOR_ADOPCIONES' if codigo=='adopcion.seguimiento' else 'ADMIN_SEGURIDAD').first()
  if rol:RP.objects.using(db).get_or_create(rol=rol,permiso=p)

class Migration(migrations.Migration):
 dependencies=[('seguridad','0010_seguimientoadopcion')]
 operations=[migrations.RunPython(cargar,migrations.RunPython.noop)]

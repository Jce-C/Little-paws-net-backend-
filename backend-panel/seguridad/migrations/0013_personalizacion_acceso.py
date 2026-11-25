from django.db import migrations

def iniciar(apps,schema_editor):
 model=apps.get_model('seguridad','ConfiguracionPanel')
 for clave,valor in {'login_fondo_opacidad':'1','login_fondo_velo':'0.12','login_fondo_posicion':'center center','login_fondo_visible':'si'}.items():model.objects.using(schema_editor.connection.alias).get_or_create(clave=clave,defaults={'valor':valor})
class Migration(migrations.Migration):
 dependencies=[('seguridad','0012_participacion_configurable')]
 operations=[migrations.RunPython(iniciar,migrations.RunPython.noop)]

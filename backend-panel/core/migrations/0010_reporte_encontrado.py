from django.db import migrations

def cargar(apps,schema_editor):
    Tipo=apps.get_model('core','TipoMaestro');Valor=apps.get_model('core','ValorMaestro');alias=schema_editor.connection.alias
    tipo=Tipo.objects.using(alias).filter(nombre='tipo_reporte').first()
    if tipo:Valor.objects.using(alias).get_or_create(tipo=tipo,nombre='Animal encontrado')

class Migration(migrations.Migration):
    dependencies=[('core','0009_ciudad_activo_ciudad_codigo_divipola')]
    operations=[migrations.RunPython(cargar,migrations.RunPython.noop)]

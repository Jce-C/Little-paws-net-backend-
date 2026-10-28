from django.db import migrations


def cargar(apps, schema_editor):
    Valor = apps.get_model("core", "ValorMaestro")
    Tipo = apps.get_model("core", "TipoMaestro")
    alias = schema_editor.connection.alias
    for tipo, nombre in (("estado_adopcion", "Retirada"),
                         ("estado_solicitud_validacion", "Correcciones"),
                         ("estado_mascota", "Con dueño")):
        maestro = Tipo.objects.using(alias).get(nombre=tipo)
        Valor.objects.using(alias).get_or_create(tipo=maestro, nombre=nombre)


class Migration(migrations.Migration):
    dependencies = [("seguridad", "0004_flujos_etapa_dos")]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]

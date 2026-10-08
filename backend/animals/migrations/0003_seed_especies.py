"""Especies y razas generales mínimas para el rescate inicial."""

from django.db import migrations


def cargar(apps, schema_editor):
    Especie = apps.get_model("animals", "Especie")
    Raza = apps.get_model("animals", "Raza")
    alias = schema_editor.connection.alias
    for nombre in ("Canino", "Felino"):
        especie, _ = Especie.objects.using(alias).get_or_create(nombre=nombre)
        Raza.objects.using(alias).get_or_create(especie=especie, nombre="Mestizo")


class Migration(migrations.Migration):
    dependencies = [("animals", "0002_documentoadjunto_autorizacionexpediente_and_more")]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]

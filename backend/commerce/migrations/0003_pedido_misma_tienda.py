"""Compatibilidad: la regla de tienda se aplica en 0005 con FK compuestas.

Algunas bases ejecutaron la version anterior y conservan sus disparadores
hasta que 0005 los retire. Las instalaciones nuevas no los crean.
"""

from django.db import migrations


def sin_operacion(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("commerce", "0002_catalogos_permisos")]
    operations = [migrations.RunPython(sin_operacion, sin_operacion)]

"""MySQL: permite muchas custodias históricas, pero solo una vigente por mascota."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("animals", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE `CustodiaMascota` "
                "ADD COLUMN `id_mascota_vigente` INT "
                "GENERATED ALWAYS AS (CASE WHEN `fecha_fin` IS NULL THEN `id_mascota` ELSE NULL END) STORED, "
                "ADD UNIQUE KEY `uq_custodia_mascota_vigente` (`id_mascota_vigente`)"
            ),
            reverse_sql=(
                "ALTER TABLE `CustodiaMascota` "
                "DROP INDEX `uq_custodia_mascota_vigente`, "
                "DROP COLUMN `id_mascota_vigente`"
            ),
        ),
    ]

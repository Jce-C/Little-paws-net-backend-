"""Corrige el orden interno de ejes de POINT en MySQL EPSG:4326.

En MySQL POINT(longitud, latitud) seguido de ST_SRID(..., 4326) coincide con
los polígonos importados con axis-order=long-lat. Comprobado por ST_Intersects.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("geography", "0002_spatial_indexes")]

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE `ReporteUbicacion` MODIFY COLUMN `punto` POINT "
                "GENERATED ALWAYS AS (ST_SRID(POINT(`longitud`, `latitud`), 4326)) "
                "STORED NOT NULL SRID 4326"
            ),
            reverse_sql=(
                "ALTER TABLE `ReporteUbicacion` MODIFY COLUMN `punto` POINT "
                "GENERATED ALWAYS AS (ST_SRID(POINT(`latitud`, `longitud`), 4326)) "
                "STORED NOT NULL SRID 4326"
            ),
        ),
    ]

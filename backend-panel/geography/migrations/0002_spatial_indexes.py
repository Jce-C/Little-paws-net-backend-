"""MySQL 8: geometrías derivadas con SRID 4326 e índices espaciales.

MySQL define los ejes de EPSG:4326 como latitud-longitud. POINT(latitud,
longitud) se normaliza internamente; ST_AsText devuelve lon-lat. Los polígonos
WKT se importan explícitamente con axis-order=long-lat.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("geography", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE `ReporteUbicacion` "
                "ADD COLUMN `punto` POINT GENERATED ALWAYS AS "
                "(ST_SRID(POINT(`latitud`, `longitud`), 4326)) STORED NOT NULL SRID 4326, "
                "ADD SPATIAL INDEX `idx_reporte_punto` (`punto`)"
            ),
            reverse_sql=(
                "ALTER TABLE `ReporteUbicacion` "
                "DROP INDEX `idx_reporte_punto`, DROP COLUMN `punto`"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "ALTER TABLE `ZonaGeografica` "
                "ADD COLUMN `geometria` MULTIPOLYGON GENERATED ALWAYS AS "
                "(ST_GeomFromText(`poligono_wkt`, 4326, 'axis-order=long-lat')) "
                "STORED NOT NULL SRID 4326, "
                "ADD SPATIAL INDEX `idx_zona_geometria` (`geometria`)"
            ),
            reverse_sql=(
                "ALTER TABLE `ZonaGeografica` "
                "DROP INDEX `idx_zona_geometria`, DROP COLUMN `geometria`"
            ),
        ),
    ]

"""Geometrías derivadas e índices espaciales en MySQL 8.

Las columnas fuente siguen siendo latitud/longitud y WKT; no se duplican
coordenadas editables. SQLite omite este DDL para pruebas aisladas.
"""

from django.db import migrations


def crear_indices(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return
    schema_editor.execute(
        "ALTER TABLE `ReporteUbicacion` "
        "ADD COLUMN `punto` POINT GENERATED ALWAYS AS "
        "(ST_SRID(POINT(`longitud`, `latitud`), 4326)) "
        "STORED NOT NULL SRID 4326, "
        "ADD SPATIAL INDEX `idx_reporte_punto` (`punto`)"
    )
    schema_editor.execute(
        "ALTER TABLE `ZonaGeografica` "
        "ADD COLUMN `geometria` MULTIPOLYGON GENERATED ALWAYS AS "
        "(ST_GeomFromText(`poligono_wkt`, 4326, 'axis-order=long-lat')) "
        "STORED NOT NULL SRID 4326, "
        "ADD SPATIAL INDEX `idx_zona_geometria` (`geometria`)"
    )


def eliminar_indices(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return
    schema_editor.execute(
        "ALTER TABLE `ZonaGeografica` "
        "DROP INDEX `idx_zona_geometria`, DROP COLUMN `geometria`"
    )
    schema_editor.execute(
        "ALTER TABLE `ReporteUbicacion` "
        "DROP INDEX `idx_reporte_punto`, DROP COLUMN `punto`"
    )


class Migration(migrations.Migration):
    dependencies = [("rescue", "0001_initial")]
    operations = [migrations.RunPython(crear_indices, eliminar_indices)]

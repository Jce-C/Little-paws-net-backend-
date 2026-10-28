"""Coordenadas fuente para geometrías MySQL derivadas e indexadas."""

from django.db import models
from django.db.models import Q

from core.models import Zona
from rescue.models import Reporte


class ReporteUbicacion(models.Model):
    reporte = models.OneToOneField(Reporte, on_delete=models.PROTECT, primary_key=True, db_column="id_reporte")
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    precision_metros = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "ReporteUbicacion"
        constraints = [
            models.CheckConstraint(condition=Q(latitud__gte=-90) & Q(latitud__lte=90), name="ck_reporte_latitud"),
            models.CheckConstraint(condition=Q(longitud__gte=-180) & Q(longitud__lte=180), name="ck_reporte_longitud"),
        ]


class ZonaGeografica(models.Model):
    zona = models.OneToOneField(Zona, on_delete=models.PROTECT, primary_key=True, db_column="id_zona")
    # WKT en orden lon-lat; la geometría MySQL es una proyección derivada e indexada.
    poligono_wkt = models.TextField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ZonaGeografica"

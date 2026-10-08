"""Entidades mínimas de mascota compartidas por rescate y adopción."""

from django.conf import settings
from django.db import models
from django.db.models import Q

from core.models import ValorMaestro


class Especie(models.Model):
    id_especie = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = "Especie"


class Raza(models.Model):
    id_raza = models.AutoField(primary_key=True)
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT, db_column="id_especie")
    nombre = models.CharField(max_length=120)

    class Meta:
        db_table = "Raza"
        constraints = [
            models.UniqueConstraint(fields=["especie", "nombre"], name="uq_raza_especie_nombre"),
        ]


class Mascota(models.Model):
    id_mascota = models.AutoField(primary_key=True)
    dueno = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_dueno", related_name="mascotas_propias",
    )
    raza = models.ForeignKey(Raza, on_delete=models.PROTECT, db_column="id_raza")
    estado_mascota = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_mascota",
        related_name="mascotas_estado",
    )
    nombre = models.CharField(max_length=120, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    es_estimada = models.BooleanField(default=False)
    sexo = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_sexo", related_name="mascotas_sexo",
    )
    tamano = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_tamano", related_name="mascotas_tamano",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Mascota"
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_nacimiento__isnull=False) | Q(es_estimada=False),
                name="ck_mascota_fecha_estimada",
            ),
        ]

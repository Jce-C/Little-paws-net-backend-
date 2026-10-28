"""Solicitudes y trazabilidad de adopción (María José)."""

from django.conf import settings
from django.db import models

from animals.models import Mascota
from core.models import ValorMaestro


class SolicitudAdopcion(models.Model):
    id_solicitud_adopcion = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, db_column="id_mascota")
    usuario_adoptante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_adoptante"
    )
    estado_adopcion = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_adopcion"
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "SolicitudAdopcion"
        indexes = [models.Index(fields=["mascota", "fecha_solicitud"], name="ix_adop_mascota_fecha")]


class HistorialEstadoAdopcion(models.Model):
    id_historial_adopcion = models.AutoField(primary_key=True)
    solicitud = models.ForeignKey(
        SolicitudAdopcion, on_delete=models.PROTECT, db_column="id_solicitud_adopcion"
    )
    estado_anterior = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_estado_anterior", related_name="adopciones_historial_anterior",
    )
    estado_nuevo = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_nuevo",
        related_name="adopciones_historial_nuevo",
    )
    usuario_actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_actor"
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)

    class Meta:
        db_table = "HistorialEstadoAdopcion"

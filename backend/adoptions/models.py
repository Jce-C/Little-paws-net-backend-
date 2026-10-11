"""Solicitudes y trazabilidad del proceso de adopción."""

from django.conf import settings
from django.db import models
from animals.models import Mascota
from core.models import ValorMaestro


class SolicitudAdopcion(models.Model):
    id_solicitud_adopcion = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, db_column="id_mascota")
    usuario_adoptante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="id_usuario_adoptante",
        related_name="solicitudes_adopcion",
    )
    estado_adopcion = models.ForeignKey(
        ValorMaestro,
        on_delete=models.PROTECT,
        db_column="id_estado_adopcion",
        related_name="solicitudes_adopcion_estado",
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "SolicitudAdopcion"
        indexes = [
            models.Index(fields=["mascota", "estado_adopcion"], name="ix_adop_mascota_estado"),
            models.Index(fields=["usuario_adoptante", "fecha_solicitud"], name="ix_adop_usuario_fecha"),
        ]


class HistorialEstadoAdopcion(models.Model):
    id_historial_adopcion = models.AutoField(primary_key=True)
    solicitud = models.ForeignKey(
        SolicitudAdopcion,
        on_delete=models.PROTECT,
        db_column="id_solicitud_adopcion",
    )
    estado_anterior = models.ForeignKey(
        ValorMaestro,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="id_estado_anterior",
        related_name="adopciones_historial_anterior",
    )
    estado_nuevo = models.ForeignKey(
        ValorMaestro,
        on_delete=models.PROTECT,
        db_column="id_estado_nuevo",
        related_name="adopciones_historial_nuevo",
    )
    usuario_actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="id_usuario_actor",
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)

    class Meta:
        db_table = "HistorialEstadoAdopcion"
        indexes = [
            models.Index(fields=["solicitud", "fecha_cambio"], name="ix_hist_adop_solicitud"),
        ]

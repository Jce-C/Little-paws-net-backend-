"""Solicitudes y trazabilidad del proceso de adopción."""

from django.conf import settings
from django.db import models
from django.db.models import F, Q

from animals.models import Mascota
from core.models import ArchivoDigital, Fundacion, ValorMaestro


class SolicitudAdopcion(models.Model):
    id_solicitud_adopcion = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, db_column="id_mascota")
    fundacion = models.ForeignKey(Fundacion, on_delete=models.PROTECT, db_column="id_fundacion")
    usuario_solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="id_usuario_solicitante",
        related_name="solicitudes_adopcion",
    )
    estado_solicitud = models.ForeignKey(
        ValorMaestro,
        on_delete=models.PROTECT,
        db_column="id_estado_solicitud",
        related_name="solicitudes_adopcion_estado",
    )
    archivo_soporte = models.ForeignKey(
        ArchivoDigital,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="id_archivo_soporte",
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    usuario_resolutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="id_usuario_resolutor",
        related_name="solicitudes_adopcion_resueltas",
    )
    observacion_solicitante = models.TextField(blank=True)
    observacion_resolucion = models.TextField(blank=True)

    class Meta:
        db_table = "SolicitudAdopcion"
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_resolucion__isnull=True) | Q(fecha_resolucion__gte=F("fecha_solicitud")),
                name="ck_solicitud_adopcion_fechas",
            ),
        ]
        indexes = [
            models.Index(fields=["mascota", "estado_solicitud"], name="ix_adop_mascota_estado"),
            models.Index(fields=["usuario_solicitante", "fecha_solicitud"], name="ix_adop_usuario_fecha"),
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

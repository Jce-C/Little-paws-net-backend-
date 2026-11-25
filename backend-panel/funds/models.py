"""Fondo externo: solo compromisos y distribuciones reportadas, sin pasarela."""

from django.conf import settings
from django.db import models
from django.db.models import Q

from core.models import ArchivoDigital, EntidadVerificable, Fundacion, ValorMaestro


class FondoExterno(models.Model):
    id_fondo_externo = models.AutoField(primary_key=True)
    entidad = models.ForeignKey(
        EntidadVerificable, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_entidad_verificable",
    )
    nombre = models.CharField(max_length=150, unique=True)
    entidad_administradora = models.CharField(max_length=150)
    tipo_fondo = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_tipo_fondo",
        related_name="fondos_tipo",
    )
    estado_fondo = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_fondo",
        related_name="fondos_estado",
    )
    datos_transferencia_cifrados = models.BinaryField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "FondoExterno"


class DonacionGeneral(models.Model):
    id_donacion = models.AutoField(primary_key=True)
    fondo_externo = models.ForeignKey(
        FondoExterno, on_delete=models.PROTECT, db_column="id_fondo_externo"
    )
    usuario_donante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_donante"
    )
    estado_donacion = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_donacion"
    )
    monto_comprometido = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_compromiso = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "DonacionGeneral"
        constraints = [
            models.CheckConstraint(condition=Q(monto_comprometido__gt=0), name="ck_don_monto_positivo"),
        ]


class HistorialEstadoDonacion(models.Model):
    id_historial_donacion = models.AutoField(primary_key=True)
    donacion = models.ForeignKey(DonacionGeneral, on_delete=models.PROTECT, db_column="id_donacion")
    estado_anterior = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_estado_anterior", related_name="donaciones_historial_anterior",
    )
    estado_nuevo = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_nuevo",
        related_name="donaciones_historial_nuevo",
    )
    usuario_actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_actor"
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)

    class Meta:
        db_table = "HistorialEstadoDonacion"


class DistribucionReportadaFondo(models.Model):
    id_distribucion = models.AutoField(primary_key=True)
    fondo_externo = models.ForeignKey(
        FondoExterno, on_delete=models.PROTECT, db_column="id_fondo_externo"
    )
    fundacion = models.ForeignKey(Fundacion, on_delete=models.PROTECT, db_column="id_fundacion")
    estado_distribucion = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_distribucion"
    )
    monto_reportado = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_distribucion = models.DateTimeField()
    criterio = models.TextField()
    usuario_confirmador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_usuario_confirmador",
    )
    archivo_evidencia = models.ForeignKey(
        ArchivoDigital, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_archivo_evidencia",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "DistribucionReportadaFondo"
        constraints = [
            models.CheckConstraint(condition=Q(monto_reportado__gt=0), name="ck_dist_monto_positivo"),
        ]


class SolicitudEmergencia(models.Model):
    id_solicitud_emergencia = models.AutoField(primary_key=True)
    fundacion = models.ForeignKey(Fundacion, on_delete=models.PROTECT, db_column="id_fundacion")
    fondo_externo = models.ForeignKey(
        FondoExterno, on_delete=models.PROTECT, db_column="id_fondo_externo"
    )
    estado_emergencia = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_emergencia"
    )
    motivo = models.TextField()
    monto_solicitado = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "SolicitudEmergencia"
        constraints = [
            models.CheckConstraint(condition=Q(monto_solicitado__gt=0), name="ck_emerg_monto_positivo"),
        ]

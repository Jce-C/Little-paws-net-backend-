"""Reportes ciudadanos, aceptación de casos y trazabilidad."""

from django.conf import settings
from django.db import models
from django.db.models import F, Q

from animals.models import Mascota
from core.models import ArchivoDigital, Fundacion, ValorMaestro, Zona


class Reporte(models.Model):
    id_reporte = models.AutoField(primary_key=True)
    usuario_reportante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_usuario_reportante",
    )
    codigo_gestion_hash = models.CharField(max_length=255, blank=True)
    tipo_reporte = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_tipo_reporte",
        related_name="reportes_tipo",
    )
    estado_reporte = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_reporte",
        related_name="reportes_estado",
    )
    mascota = models.ForeignKey(
        Mascota, on_delete=models.PROTECT, null=True, blank=True, db_column="id_mascota",
    )
    descripcion = models.TextField()
    contacto_reportante = models.CharField(max_length=150, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Reporte"
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(usuario_reportante__isnull=False, codigo_gestion_hash="")
                    | (Q(usuario_reportante__isnull=True) & ~Q(codigo_gestion_hash=""))
                ),
                name="ck_reporte_identidad",
            ),
        ]


class ReporteUbicacion(models.Model):
    reporte = models.OneToOneField(
        Reporte, on_delete=models.PROTECT, primary_key=True, db_column="id_reporte",
    )
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
    poligono_wkt = models.TextField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ZonaGeografica"


class HistorialEstadoReporte(models.Model):
    id_historial_reporte = models.AutoField(primary_key=True)
    reporte = models.ForeignKey(Reporte, on_delete=models.PROTECT, db_column="id_reporte")
    estado_anterior = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_estado_anterior", related_name="reportes_historial_anterior",
    )
    estado_nuevo = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_nuevo",
        related_name="reportes_historial_nuevo",
    )
    usuario_actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_usuario_actor",
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)

    class Meta:
        db_table = "HistorialEstadoReporte"


class CasoRescate(models.Model):
    id_caso = models.AutoField(primary_key=True)
    reporte = models.OneToOneField(Reporte, on_delete=models.PROTECT, db_column="id_reporte")
    fundacion = models.ForeignKey(Fundacion, on_delete=models.PROTECT, db_column="id_fundacion")
    estado_caso = models.ForeignKey(ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_caso")
    fecha_aceptacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    justificacion_sin_cupo = models.TextField(blank=True)
    ocupa_cupo = models.BooleanField(default=True)
    usuario_ultimo_cambio = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_ultimo_cambio",
    )

    class Meta:
        db_table = "CasoRescate"
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_cierre__isnull=True) | Q(fecha_cierre__gte=F("fecha_aceptacion")),
                name="ck_caso_fechas",
            ),
        ]


class HistorialEstadoCaso(models.Model):
    id_historial = models.AutoField(primary_key=True)
    caso = models.ForeignKey(CasoRescate, on_delete=models.PROTECT, db_column="id_caso")
    estado_anterior = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_estado_anterior", related_name="casos_historial_anterior",
    )
    estado_nuevo = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_nuevo",
        related_name="casos_historial_nuevo",
    )
    usuario_actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_actor",
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)

    class Meta:
        db_table = "HistorialEstadoCaso"


class EvidenciaCaso(models.Model):
    id_evidencia = models.AutoField(primary_key=True)
    caso = models.ForeignKey(CasoRescate, on_delete=models.PROTECT, db_column="id_caso")
    archivo = models.OneToOneField(ArchivoDigital, on_delete=models.PROTECT, db_column="id_archivo")
    tipo_evidencia = models.ForeignKey(ValorMaestro, on_delete=models.PROTECT, db_column="id_tipo_evidencia")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "EvidenciaCaso"


class CuentaFundacion(models.Model):
    id_cuenta = models.AutoField(primary_key=True)
    fundacion = models.ForeignKey(Fundacion, on_delete=models.PROTECT, db_column="id_fundacion")
    numero_cuenta_cifrado = models.BinaryField()
    numero_cuenta_ultimos4 = models.CharField(max_length=4)
    banco = models.CharField(max_length=120)
    tipo_cuenta = models.CharField(max_length=60)
    titular = models.CharField(max_length=150)
    activa = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "CuentaFundacion"


class Apadrinamiento(models.Model):
    id_apadrinamiento = models.AutoField(primary_key=True)
    reporte = models.ForeignKey(Reporte, on_delete=models.PROTECT, db_column="id_reporte")
    usuario_padrino = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_padrino",
    )
    estado_apadrinamiento = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_apadrinamiento",
    )
    monto_comprometido = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_compromiso = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)

    class Meta:
        db_table = "Apadrinamiento"
        constraints = [
            models.CheckConstraint(condition=Q(monto_comprometido__gt=0), name="ck_apad_monto_positivo"),
        ]


class CuentaRevelada(models.Model):
    id_cuenta_revelada = models.AutoField(primary_key=True)
    apadrinamiento = models.ForeignKey(
        Apadrinamiento, on_delete=models.PROTECT, db_column="id_apadrinamiento",
    )
    cuenta = models.ForeignKey(CuentaFundacion, on_delete=models.PROTECT, db_column="id_cuenta")
    fecha_revelacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "CuentaRevelada"
        constraints = [
            models.UniqueConstraint(fields=["apadrinamiento", "cuenta"], name="uq_cuenta_revelada"),
        ]


class DeclaracionTransferencia(models.Model):
    """Declaración del padrino, no confirmación de recepción."""

    id_declaracion = models.AutoField(primary_key=True)
    apadrinamiento = models.ForeignKey(
        Apadrinamiento, on_delete=models.PROTECT, db_column="id_apadrinamiento",
    )
    monto_declarado = models.DecimalField(max_digits=12, decimal_places=2)
    referencia_cifrada = models.BinaryField(null=True, blank=True)
    evidencia = models.ForeignKey(
        ArchivoDigital, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_archivo_evidencia",
    )
    fecha_transferencia_declarada = models.DateTimeField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "DeclaracionTransferencia"
        constraints = [
            models.CheckConstraint(condition=Q(monto_declarado__gt=0), name="ck_decl_monto_positivo"),
        ]


class ConfirmacionAporte(models.Model):
    id_confirmacion = models.AutoField(primary_key=True)
    apadrinamiento = models.ForeignKey(
        Apadrinamiento, on_delete=models.PROTECT, db_column="id_apadrinamiento",
    )
    monto_confirmado = models.DecimalField(max_digits=12, decimal_places=2)
    usuario_confirmador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_confirmador",
    )
    fecha_confirmacion = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)

    class Meta:
        db_table = "ConfirmacionAporte"
        constraints = [
            models.CheckConstraint(condition=Q(monto_confirmado__gt=0), name="ck_conf_monto_positivo"),
        ]


class HistorialEstadoApadrinamiento(models.Model):
    id_historial_apadrinamiento = models.AutoField(primary_key=True)
    apadrinamiento = models.ForeignKey(
        Apadrinamiento, on_delete=models.PROTECT, db_column="id_apadrinamiento",
    )
    estado_anterior = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_estado_anterior", related_name="apadrinamientos_historial_anterior",
    )
    estado_nuevo = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_nuevo",
        related_name="apadrinamientos_historial_nuevo",
    )
    usuario_actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_actor",
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)

    class Meta:
        db_table = "HistorialEstadoApadrinamiento"

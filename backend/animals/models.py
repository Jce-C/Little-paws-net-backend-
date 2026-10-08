"""Entidades mínimas de mascota compartidas por rescate y adopción."""

from django.conf import settings
from django.db import models
from django.db.models import F, Q

from core.models import ArchivoDigital, Fundacion, ValorMaestro, Veterinario


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


class CustodiaMascota(models.Model):
    id_custodia = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, db_column="id_mascota")
    fundacion = models.ForeignKey(Fundacion, on_delete=models.PROTECT, db_column="id_fundacion")
    caso = models.ForeignKey(
        "rescue.CasoRescate", on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_caso_origen",
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    usuario_registrador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_registrador",
    )

    class Meta:
        db_table = "CustodiaMascota"
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=F("fecha_inicio")),
                name="ck_custodia_fechas",
            ),
        ]


class AutorizacionExpediente(models.Model):
    id_autorizacion = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, db_column="id_mascota")
    veterinario = models.ForeignKey(Veterinario, on_delete=models.PROTECT, db_column="id_veterinario")
    usuario_otorgante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_otorgante",
    )
    fecha_otorgamiento = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    fecha_revocacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "AutorizacionExpediente"
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_expiracion__gt=F("fecha_otorgamiento")),
                name="ck_autorizacion_vigencia",
            ),
            models.CheckConstraint(
                condition=Q(fecha_revocacion__isnull=True) | Q(fecha_revocacion__gte=F("fecha_otorgamiento")),
                name="ck_autorizacion_revocacion",
            ),
        ]


class CodigoQRExpediente(models.Model):
    id_qr = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, db_column="id_mascota")
    codigo_hash = models.CharField(max_length=64, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    fecha_revocacion = models.DateTimeField(null=True, blank=True)
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_creador",
    )

    class Meta:
        db_table = "CodigoQRExpediente"
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_expiracion__gt=F("fecha_creacion")),
                name="ck_qr_vigencia",
            ),
        ]


class HistorialMedico(models.Model):
    id_historial_medico = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, db_column="id_mascota")
    detalle = models.TextField()
    veterinario = models.ForeignKey(
        Veterinario, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_veterinario",
    )
    usuario_registrador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        db_column="id_usuario_registrador", related_name="registros_medicos_creados",
    )
    usuario_verificador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_usuario_verificador", related_name="registros_medicos_verificados",
    )
    nombre_veterinario_externo = models.CharField(max_length=150, blank=True)
    registro_profesional_externo = models.CharField(max_length=80, blank=True)
    fecha_atencion = models.DateTimeField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "HistorialMedico"
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(veterinario__isnull=False, nombre_veterinario_externo="", registro_profesional_externo="")
                    | (
                        Q(veterinario__isnull=True, usuario_verificador__isnull=False)
                        & ~Q(nombre_veterinario_externo="")
                        & ~Q(registro_profesional_externo="")
                    )
                ),
                name="ck_medico_profesional",
            ),
        ]


class DocumentoAdjunto(models.Model):
    id_documento = models.AutoField(primary_key=True)
    archivo = models.OneToOneField(ArchivoDigital, on_delete=models.PROTECT, db_column="id_archivo")
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, db_column="id_mascota")
    tipo_documento = models.ForeignKey(ValorMaestro, on_delete=models.PROTECT, db_column="id_tipo_documento")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "DocumentoAdjunto"

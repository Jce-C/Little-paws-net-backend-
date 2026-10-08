"""Catálogos, autorización de negocio y entidades compartidas de V2."""

from django.conf import settings
from django.db import models
from django.db.models import F, Q


class TipoMaestro(models.Model):
    id_tipo_maestro = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "TipoMaestro"


class ValorMaestro(models.Model):
    id_valor_maestro = models.AutoField(primary_key=True)
    tipo = models.ForeignKey(TipoMaestro, on_delete=models.PROTECT, db_column="id_tipo_maestro")
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = "ValorMaestro"
        constraints = [
            models.UniqueConstraint(fields=["tipo", "nombre"], name="uq_valor_tipo_nombre"),
        ]


class Rol(models.Model):
    class Ambito(models.TextChoices):
        GLOBAL = "GLOBAL", "Global"
        ENTIDAD = "ENTIDAD", "Entidad"

    id_rol = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=255, blank=True)
    ambito = models.CharField(max_length=7, choices=Ambito.choices)

    class Meta:
        db_table = "Rol"
        constraints = [
            models.CheckConstraint(
                condition=Q(ambito__in=["GLOBAL", "ENTIDAD"]),
                name="ck_rol_ambito",
            ),
        ]


class Permiso(models.Model):
    id_permiso = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=80, unique=True)
    descripcion = models.CharField(max_length=255)

    class Meta:
        db_table = "Permiso"


class RolPermiso(models.Model):
    id_rol_permiso = models.AutoField(primary_key=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, db_column="id_rol")
    permiso = models.ForeignKey(Permiso, on_delete=models.PROTECT, db_column="id_permiso")

    class Meta:
        db_table = "RolPermiso"
        constraints = [
            models.UniqueConstraint(fields=["rol", "permiso"], name="uq_rol_permiso"),
        ]


class UsuarioRol(models.Model):
    id_usuario_rol = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario")
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, db_column="id_rol")
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_revocacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "UsuarioRol"
        constraints = [
            models.UniqueConstraint(fields=["usuario", "rol"], name="uq_usuario_rol"),
            models.CheckConstraint(
                condition=Q(fecha_revocacion__isnull=True) | Q(fecha_revocacion__gte=F("fecha_asignacion")),
                name="ck_usuario_rol_fechas",
            ),
        ]


class ArchivoDigital(models.Model):
    id_archivo = models.AutoField(primary_key=True)
    class Visibilidad(models.TextChoices):
        PUBLICO = "PUBLICO", "Público"
        PRIVADO = "PRIVADO", "Privado"

    storage_key = models.CharField(max_length=255, unique=True)
    url_archivo = models.URLField(max_length=2048, blank=True)
    mime_type = models.CharField(max_length=120)
    tamano_bytes = models.PositiveBigIntegerField()
    visibilidad = models.CharField(max_length=7, choices=Visibilidad.choices, default=Visibilidad.PRIVADO)
    usuario_cargador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, db_column="id_usuario_cargador"
    )
    fecha_carga = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ArchivoDigital"


class Ciudad(models.Model):
    id_ciudad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    departamento = models.CharField(max_length=120)

    class Meta:
        db_table = "Ciudad"
        constraints = [
            models.UniqueConstraint(fields=["departamento", "nombre"], name="uq_ciudad_departamento_nombre"),
        ]


class Zona(models.Model):
    id_zona = models.AutoField(primary_key=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, db_column="id_ciudad")
    nombre = models.CharField(max_length=120)

    class Meta:
        db_table = "Zona"
        constraints = [
            models.UniqueConstraint(fields=["ciudad", "nombre"], name="uq_zona_ciudad_nombre"),
        ]


class EntidadVerificable(models.Model):
    id_entidad_verificable = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    estado_verificacion = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_verificacion"
    )

    class Meta:
        db_table = "EntidadVerificable"


class EntidadMiembro(models.Model):
    id_entidad_miembro = models.AutoField(primary_key=True)
    entidad = models.ForeignKey(
        EntidadVerificable, on_delete=models.PROTECT, db_column="id_entidad_verificable"
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario")
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_salida = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "EntidadMiembro"
        constraints = [
            models.UniqueConstraint(fields=["entidad", "usuario"], name="uq_entidad_miembro"),
            models.CheckConstraint(
                condition=Q(fecha_salida__isnull=True) | Q(fecha_salida__gte=F("fecha_ingreso")),
                name="ck_entidad_miembro_fechas",
            ),
        ]


class EntidadMiembroRol(models.Model):
    id_entidad_miembro_rol = models.AutoField(primary_key=True)
    miembro = models.ForeignKey(EntidadMiembro, on_delete=models.PROTECT, db_column="id_entidad_miembro")
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, db_column="id_rol")

    class Meta:
        db_table = "EntidadMiembroRol"
        constraints = [
            models.UniqueConstraint(fields=["miembro", "rol"], name="uq_entidad_miembro_rol"),
        ]


class Fundacion(models.Model):
    entidad = models.OneToOneField(
        EntidadVerificable, on_delete=models.PROTECT, primary_key=True, db_column="id_entidad_verificable"
    )
    nit = models.CharField(max_length=30, unique=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, db_column="id_ciudad")
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = "Fundacion"


class Clinica(models.Model):
    entidad = models.OneToOneField(
        EntidadVerificable, on_delete=models.PROTECT, primary_key=True, db_column="id_entidad_verificable"
    )
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, db_column="id_ciudad")
    direccion = models.CharField(max_length=255)

    class Meta:
        db_table = "Clinica"


class Veterinario(models.Model):
    entidad = models.OneToOneField(
        EntidadVerificable, on_delete=models.PROTECT, primary_key=True, db_column="id_entidad_verificable"
    )
    usuario_profesional = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_profesional"
    )
    clinica = models.ForeignKey(Clinica, on_delete=models.PROTECT, null=True, blank=True, db_column="id_clinica")
    registro_profesional = models.CharField(max_length=80, unique=True)
    especialidad = models.CharField(max_length=120, blank=True)

    class Meta:
        db_table = "Veterinario"


class Tienda(models.Model):
    entidad = models.OneToOneField(
        EntidadVerificable, on_delete=models.PROTECT, primary_key=True, db_column="id_entidad_verificable"
    )
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, db_column="id_ciudad")
    direccion = models.CharField(max_length=255)
    whatsapp = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = "Tienda"


class Anunciante(models.Model):
    entidad = models.OneToOneField(
        EntidadVerificable, on_delete=models.PROTECT, primary_key=True, db_column="id_entidad_verificable"
    )
    nit_documento = models.CharField(max_length=30, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = "Anunciante"


class FundacionZona(models.Model):
    id_fundacion_zona = models.AutoField(primary_key=True)
    fundacion = models.ForeignKey(Fundacion, on_delete=models.PROTECT, db_column="id_fundacion")
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT, db_column="id_zona")
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "FundacionZona"
        constraints = [
            models.UniqueConstraint(fields=["fundacion", "zona"], name="uq_fundacion_zona"),
        ]


class CapacidadFundacion(models.Model):
    id_capacidad = models.AutoField(primary_key=True)
    fundacion = models.OneToOneField(Fundacion, on_delete=models.PROTECT, db_column="id_fundacion")
    cupos_totales = models.PositiveSmallIntegerField()
    cupos_ocupados = models.PositiveSmallIntegerField(default=0)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario_actualizador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_actualizador"
    )

    class Meta:
        db_table = "CapacidadFundacion"
        constraints = [
            models.CheckConstraint(
                condition=Q(cupos_ocupados__lte=F("cupos_totales")),
                name="ck_capacidad_cupos",
            ),
        ]


class SolicitudValidacion(models.Model):
    id_solicitud_validacion = models.AutoField(primary_key=True)
    entidad = models.ForeignKey(
        EntidadVerificable, on_delete=models.PROTECT, db_column="id_entidad_verificable"
    )
    usuario_solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        db_column="id_usuario_solicitante", related_name="validaciones_solicitadas",
    )
    usuario_validador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        db_column="id_usuario_validador", related_name="validaciones_resueltas",
    )
    estado_solicitud = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_estado_solicitud"
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    observacion = models.TextField(blank=True)

    class Meta:
        db_table = "SolicitudValidacion"
        constraints = [
            models.CheckConstraint(
                condition=Q(fecha_resolucion__isnull=True) | Q(fecha_resolucion__gte=F("fecha_solicitud")),
                name="ck_validacion_fechas",
            ),
        ]


class DocumentoValidacion(models.Model):
    id_documento_validacion = models.AutoField(primary_key=True)
    solicitud = models.ForeignKey(
        SolicitudValidacion, on_delete=models.PROTECT, db_column="id_solicitud_validacion"
    )
    archivo = models.OneToOneField(ArchivoDigital, on_delete=models.PROTECT, db_column="id_archivo")
    usuario_cargador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario_cargador"
    )
    fecha_carga = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "DocumentoValidacion"


class Notificacion(models.Model):
    """Bandeja interna: no implica entrega por correo o WhatsApp."""

    id_notificacion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column="id_usuario")
    tipo_notificacion = models.ForeignKey(
        ValorMaestro, on_delete=models.PROTECT, db_column="id_tipo_notificacion"
    )
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "Notificacion"
        indexes = [models.Index(fields=["usuario", "fecha_creacion"], name="ix_notif_usuario_fecha")]


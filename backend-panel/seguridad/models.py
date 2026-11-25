from django.conf import settings
from django.db import models
from django.db.models import F, Q


class EventoSeguridad(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=80)
    recurso = models.CharField(max_length=60)
    objeto_id = models.PositiveBigIntegerField(null=True)
    entidad = models.ForeignKey("core.EntidadVerificable", on_delete=models.PROTECT, null=True)
    motivo = models.CharField(max_length=500, blank=True)
    datos = models.JSONField(default=dict)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "EventoSeguridad"
        ordering = ["-pk"]
        indexes = [models.Index(fields=['fecha'],name='audit_fecha_idx'),models.Index(fields=['actor','fecha'],name='audit_actor_fecha_idx'),models.Index(fields=['recurso','fecha'],name='audit_recurso_fecha_idx')]


class BajaAdministrativa(models.Model):
    """Reversible logical removal; never deletes domain records or history."""
    tipo=models.CharField(max_length=16,choices=[('usuarios','Usuarios'),('roles','Roles'),('entidades','Entidades'),('productos','Productos')])
    objeto_id=models.PositiveBigIntegerField()
    activo=models.BooleanField(default=False)
    eliminado=models.BooleanField(default=False)
    autor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    motivo=models.CharField(max_length=500)
    actualizada=models.DateTimeField(auto_now=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['tipo','objeto_id'],name='uq_baja_objeto')]


class OperacionAdministrativa(models.Model):
    id=models.UUIDField(primary_key=True)
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    tipo=models.CharField(max_length=16)
    objeto_id=models.PositiveBigIntegerField()
    accion=models.CharField(max_length=16)
    resultado=models.JSONField(default=dict)
    fecha=models.DateTimeField(auto_now_add=True)


class ResponsableEntidad(models.Model):
    # Una sola fila de coordinación por entidad: también es el bloqueo de sus cambios.
    entidad = models.OneToOneField("core.EntidadVerificable", on_delete=models.PROTECT)
    principal = models.ForeignKey("core.EntidadMiembro", on_delete=models.PROTECT)

    class Meta:
        db_table = "ResponsableEntidad"


class TransferenciaResponsabilidad(models.Model):
    entidad = models.ForeignKey("core.EntidadVerificable", on_delete=models.PROTECT)
    saliente = models.ForeignKey("core.EntidadMiembro", on_delete=models.PROTECT, related_name="transferencias_salientes")
    sucesor = models.ForeignKey("core.EntidadMiembro", on_delete=models.PROTECT, related_name="transferencias_entrantes")
    mantener_secundario = models.BooleanField(default=False)
    estado = models.CharField(max_length=10, choices=[("PENDIENTE", "Pendiente"), ("ACEPTADA", "Aceptada"), ("CANCELADA", "Cancelada")], default="PENDIENTE")
    creada = models.DateTimeField(auto_now_add=True)
    resuelta = models.DateTimeField(null=True)

    class Meta:
        db_table = "TransferenciaResponsabilidad"
        constraints = [models.CheckConstraint(condition=~Q(saliente=F("sucesor")), name="ck_transferencia_personas_distintas")]


class AsignacionRecurso(models.Model):
    """Asignación actual; su historial permanece en EventoSeguridad."""

    recurso = models.ForeignKey("core.Recurso", on_delete=models.PROTECT)
    objeto_id = models.PositiveBigIntegerField()
    entidad = models.ForeignKey("core.EntidadVerificable", on_delete=models.PROTECT, null=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_revocacion = models.DateTimeField(null=True)

    class Meta:
        db_table = "AsignacionRecurso"
        constraints = [models.UniqueConstraint(fields=["recurso", "objeto_id"], name="uq_asignacion_objeto")]


class AsignacionFondo(models.Model):
    # Los fondos admiten varios gestores; la exclusividad solo corresponde a colas.
    fondo = models.ForeignKey("funds.FondoExterno", on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_revocacion = models.DateTimeField(null=True)

    class Meta:
        db_table = "AsignacionGestorFondo"
        constraints = [models.UniqueConstraint(fields=["fondo", "usuario"], name="uq_gestor_fondo")]


class DelegacionCuenta(models.Model):
    entidad = models.ForeignKey("core.EntidadVerificable", on_delete=models.PROTECT)
    miembro = models.OneToOneField("core.EntidadMiembro", on_delete=models.PROTECT)
    otorgante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    revocada = models.DateTimeField(null=True)


class PropuestaCuenta(models.Model):
    entidad = models.ForeignKey("core.EntidadVerificable", on_delete=models.PROTECT)
    preparador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    numero_cifrado = models.BinaryField()
    ultimos4 = models.CharField(max_length=4)
    banco = models.CharField(max_length=120)
    tipo = models.CharField(max_length=60)
    titular = models.CharField(max_length=150)
    estado = models.CharField(max_length=12, default="PENDIENTE")
    cuenta_base_id = models.PositiveIntegerField(null=True)
    cuenta_publicada = models.ForeignKey("rescue.CuentaFundacion", on_delete=models.PROTECT, null=True)
    creada = models.DateTimeField(auto_now_add=True)


class AccesoExcepcional(models.Model):
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="excepciones_solicitadas")
    aprobador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name="excepciones_aprobadas")
    recurso = models.CharField(max_length=40)
    objeto_id = models.PositiveIntegerField()
    motivo = models.CharField(max_length=500)
    estado = models.CharField(max_length=12, default="PENDIENTE")
    aprobada = models.DateTimeField(null=True)
    expira = models.DateTimeField(null=True)
    revocada = models.DateTimeField(null=True)


class DocumentoPrivado(models.Model):
    """Solo metadatos: el contenido vive fuera de static/media públicos."""
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    recurso = models.CharField(max_length=40)
    objeto_id = models.PositiveIntegerField()
    clave = models.CharField(max_length=80, unique=True)
    mime = models.CharField(max_length=50)
    tamano = models.PositiveIntegerField()
    sha256 = models.CharField(max_length=64)
    creada = models.DateTimeField(auto_now_add=True)


class EnmiendaClinica(models.Model):
    original = models.ForeignKey("animals.HistorialMedico", on_delete=models.PROTECT)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    detalle = models.TextField()
    motivo = models.CharField(max_length=500)
    creada = models.DateTimeField(auto_now_add=True)


class RevisionSoporte(models.Model):
    documento = models.ForeignKey(DocumentoPrivado, on_delete=models.PROTECT)
    profesional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    resultado = models.CharField(max_length=15)
    observacion = models.CharField(max_length=500)
    creada = models.DateTimeField(auto_now_add=True)


class CorreccionReporte(models.Model):
    reporte = models.ForeignKey("rescue.Reporte", on_delete=models.PROTECT)
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    propuesta = models.JSONField()
    base = models.JSONField()
    motivo = models.CharField(max_length=500)
    estado = models.CharField(max_length=12, default="PENDIENTE")
    creada = models.DateTimeField(auto_now_add=True)


class PublicacionReporte(models.Model):
    reporte = models.OneToOneField("rescue.Reporte", on_delete=models.PROTECT)
    oculta = models.BooleanField(default=False)
    revision_pendiente = models.BooleanField(default=False)


class RespuestasAdopcion(models.Model):
    solicitud = models.OneToOneField("adoption.SolicitudAdopcion", on_delete=models.PROTECT)
    respuestas = models.JSONField(default=dict)


class VersionRespuestas(models.Model):
    solicitud = models.ForeignKey("adoption.SolicitudAdopcion", on_delete=models.PROTECT)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    anteriores = models.JSONField()
    nuevas = models.JSONField()
    creada = models.DateTimeField(auto_now_add=True)


class Anuncio(models.Model):
    entidad = models.ForeignKey("core.EntidadVerificable", on_delete=models.PROTECT)
    oculto = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)


class VersionAnuncio(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.PROTECT)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    titulo = models.CharField(max_length=150)
    texto = models.CharField(max_length=1000)
    url = models.URLField(max_length=2048)
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    estado = models.CharField(max_length=12, default="PENDIENTE")
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(fin__gt=F("inicio")), name="ck_version_anuncio_fechas")]


class ReclamacionMascota(models.Model):
    mascota = models.ForeignKey("animals.Mascota", on_delete=models.PROTECT)
    reclamante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reclamaciones")
    revisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name="reclamaciones_asignadas")
    motivo = models.CharField(max_length=500)
    estado = models.CharField(max_length=12, default="PENDIENTE")
    creada = models.DateTimeField(auto_now_add=True)
    dueno_revisado_id = models.PositiveIntegerField(null=True)


class HistorialTitularidad(models.Model):
    reclamacion = models.OneToOneField(ReclamacionMascota, on_delete=models.PROTECT)
    anterior = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name="titularidades_entregadas")
    nuevo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="titularidades_recibidas")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="titularidades_revisadas")
    motivo = models.CharField(max_length=500)
    creada = models.DateTimeField(auto_now_add=True)


class CambioProducto(models.Model):
    producto = models.ForeignKey("commerce.Producto", on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    anteriores = models.JSONField()
    nuevos = models.JSONField()
    creada = models.DateTimeField(auto_now_add=True)


class DesafioWeb(models.Model):
    token = models.UUIDField(primary_key=True)
    sesion_hash = models.CharField(max_length=64)
    respuesta_hash = models.CharField(max_length=64)
    expira = models.DateTimeField(db_index=True)
    consumido = models.BooleanField(default=False)


class LimiteWeb(models.Model):
    clave = models.CharField(max_length=64, primary_key=True)
    ventana = models.PositiveBigIntegerField()
    cantidad = models.PositiveIntegerField(default=0)


class ExcepcionPermiso(models.Model):
    """Una excepción efectiva por persona/permiso/contexto; HEREDAR elimina la fila."""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    permiso = models.ForeignKey('core.Permiso', on_delete=models.PROTECT)
    entidad = models.ForeignKey('core.EntidadVerificable', null=True, blank=True, on_delete=models.PROTECT)
    contexto_id = models.PositiveIntegerField(default=0)
    efecto = models.CharField(max_length=8, choices=[('PERMITIR', 'Permitir'), ('DENEGAR', 'Denegar')])
    motivo = models.CharField(max_length=500)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='excepciones_otorgadas', on_delete=models.PROTECT)
    expira = models.DateTimeField(null=True, blank=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'permiso', 'contexto_id'], name='uq_excepcion_usuario_permiso_contexto'),
            models.CheckConstraint(condition=Q(efecto__in=['PERMITIR', 'DENEGAR']), name='ck_excepcion_efecto'),
            models.CheckConstraint(condition=Q(entidad__isnull=True, contexto_id=0) | Q(entidad_id=F('contexto_id'), contexto_id__gt=0), name='ck_excepcion_contexto'),
        ]


class RevisionPanel(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1)
    version = models.PositiveBigIntegerField(default=0)


class PreferenciaUsuario(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    perfil_visual = models.CharField(max_length=40, default='ciudadano')


class ConfiguracionPanel(models.Model):
    clave = models.CharField(max_length=50, unique=True)
    valor = models.CharField(max_length=500)


class SeguimientoAdopcion(models.Model):
    solicitud = models.ForeignKey('adoption.SolicitudAdopcion',on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    detalle = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

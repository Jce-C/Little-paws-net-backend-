"""Servicios transaccionales: la interfaz no decide los ámbitos ni las entidades."""
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from accounts.models import Usuario
from core.models import EntidadMiembro, EntidadMiembroRol, EntidadVerificable, Rol, UsuarioRol
from .autorizacion import exigir, principal_de, puede, tiene_base, usuario_activo
from .models import AsignacionFondo, AsignacionRecurso, EventoSeguridad, ResponsableEntidad, TransferenciaResponsabilidad
from .objetos import contexto


def auditar(actor, accion, recurso, objeto_id=None, entidad_id=None, motivo="", **datos):
    # Solo metadatos explícitos de cada servicio. Nunca request.data, contraseñas o cuentas.
    return EventoSeguridad.objects.create(actor_id=getattr(actor, "pk", actor), accion=accion,
        recurso=recurso, objeto_id=objeto_id, entidad_id=entidad_id, motivo=motivo[:500], datos=datos)


def motivo_obligatorio(motivo):
    if not isinstance(motivo, str) or not motivo.strip() or len(motivo) > 500:
        raise ValidationError("Indica un motivo de hasta 500 caracteres")
    return motivo.strip()


def bloqueo_seguridad():
    return Rol.objects.select_for_update().get(codigo="ADMIN_SEGURIDAD")


def conservar_administrador(usuario_id=None):
    qs = UsuarioRol.objects.filter(rol__codigo="ADMIN_SEGURIDAD", rol__activo=True,
                                  usuario__is_active=True, fecha_revocacion__isnull=True)
    if usuario_id is not None:
        qs = qs.exclude(usuario_id=usuario_id)
    if not qs.exists():
        raise ValidationError("No se puede retirar el último Administrador de seguridad activo")


def es_responsable(actor, entidad_id):
    return principal_de(actor, entidad_id) or (tiene_base(actor, "miembros.roles", entidad_id=entidad_id)
        and EntidadMiembroRol.objects.filter(miembro__usuario_id=actor.pk,
            miembro__entidad_id=entidad_id, miembro__fecha_salida__isnull=True,
            fecha_revocacion__isnull=True, rol__codigo="RESPONSABLE_SECUNDARIO", rol__activo=True).exists())


def exigir_responsable(actor, entidad_id):
    exigir(actor, "miembros.roles", entidad_id=entidad_id)
    if not es_responsable(actor, entidad_id):
        raise PermissionDenied("La operación requiere responsabilidad vigente en esta entidad")


def limpiar_asignaciones(usuario_id):
    """Retirar asignaciones que ya no tienen el permiso base; no reasignar por reloj."""
    for asignacion in AsignacionRecurso.objects.select_related("recurso").filter(
        usuario_id=usuario_id, fecha_revocacion__isnull=True):
        codigo = "fondo.reportar_distribucion" if asignacion.recurso.codigo == "fondo" else f"{asignacion.recurso.codigo}.tomar"
        if not tiene_base(usuario_id, codigo, entidad_id=asignacion.entidad_id):
            asignacion.fecha_revocacion = timezone.now()
            asignacion.save(update_fields=["fecha_revocacion"])
    for asignacion in AsignacionFondo.objects.select_related("fondo").filter(
        usuario_id=usuario_id, fecha_revocacion__isnull=True):
        if not tiene_base(usuario_id, "fondo.reportar_distribucion", entidad_id=asignacion.fondo.entidad_id):
            asignacion.fecha_revocacion = timezone.now()
            asignacion.save(update_fields=["fecha_revocacion"])


@transaction.atomic
def asignar_global(actor, usuario_id, rol_id, *, revocar=False, motivo=""):
    bloqueo_seguridad()
    exigir(actor, "roles.asignar")
    usuario = Usuario.objects.select_for_update().get(pk=usuario_id)
    rol = Rol.objects.get(pk=rol_id, activo=True, ambito="GLOBAL")
    if not revocar and not usuario.is_active:
        raise ValidationError("Activa la cuenta antes de asignar un rol")
    if rol.codigo == "ADMIN_SEGURIDAD" and revocar:
        conservar_administrador(usuario.pk)
    asignacion, _ = UsuarioRol.objects.get_or_create(usuario=usuario, rol=rol)
    asignacion.fecha_revocacion = timezone.now() if revocar else None
    asignacion.save(update_fields=["fecha_revocacion"])
    limpiar_asignaciones(usuario.pk)
    auditar(actor, "rol_global.revocar" if revocar else "rol_global.asignar", "usuarios", usuario.pk,
            motivo=motivo, rol_id=rol.pk)
    return asignacion


@transaction.atomic
def guardar_estado_usuario(actor, usuario, datos):
    bloqueo_seguridad()
    exigir(actor, "usuarios.editar")
    usuario = Usuario.objects.select_for_update().get(pk=usuario.pk)
    if datos.get("is_active") is False:
        if ResponsableEntidad.objects.filter(principal__usuario=usuario,
            principal__fecha_salida__isnull=True).exists():
            raise ValidationError("Transfiere o recupera la responsabilidad principal antes de esta baja ordinaria")
        if UsuarioRol.objects.filter(usuario=usuario, rol__codigo="ADMIN_SEGURIDAD", fecha_revocacion__isnull=True).exists():
            conservar_administrador(usuario.pk)
    for clave, valor in datos.items():
        setattr(usuario, clave, valor)
    usuario.save()
    limpiar_asignaciones(usuario.pk)
    auditar(actor, "usuario.editar", "usuarios", usuario.pk, campos=sorted(datos))
    return usuario


@transaction.atomic
def designar_principal(actor, entidad_id, usuario_id, *, recuperar=False, motivo=""):
    exigir(actor, "principal.designar")
    EntidadVerificable.objects.select_for_update().get(pk=entidad_id)
    usuario = Usuario.objects.select_for_update().get(pk=usuario_id, is_active=True)
    actual = ResponsableEntidad.objects.filter(entidad_id=entidad_id).first()
    if actual and not recuperar:
        raise ValidationError("La entidad ya tiene principal: utiliza transferencia o recuperación")
    if recuperar:
        motivo = motivo_obligatorio(motivo)
    miembro, _ = EntidadMiembro.objects.get_or_create(entidad_id=entidad_id, usuario=usuario)
    if miembro.fecha_salida is not None:
        raise ValidationError("La persona debe tener membresía vigente")
    anterior = actual.principal_id if actual else None
    registro, _ = ResponsableEntidad.objects.update_or_create(entidad_id=entidad_id, defaults={"principal": miembro})
    TransferenciaResponsabilidad.objects.filter(entidad_id=entidad_id, estado="PENDIENTE").update(
        estado="CANCELADA", resuelta=timezone.now())
    auditar(actor, "principal.recuperar" if recuperar else "principal.designar", "entidades",
            entidad_id, entidad_id, motivo, anterior=anterior, principal_id=miembro.pk)
    return registro


@transaction.atomic
def gestionar_miembro(actor, entidad_id, usuario_id, *, retirar=False):
    EntidadVerificable.objects.select_for_update().get(pk=entidad_id)
    exigir_responsable(actor, entidad_id)
    usuario = Usuario.objects.select_for_update().get(pk=usuario_id, is_active=True)
    miembro, _ = EntidadMiembro.objects.get_or_create(entidad_id=entidad_id, usuario=usuario)
    if retirar and ResponsableEntidad.objects.filter(entidad_id=entidad_id, principal=miembro).exists():
        raise ValidationError("El principal debe transferir antes de salir de la entidad")
    # Reingresar no reactiva cargos antiguos ni asignaciones previas.
    if retirar or miembro.fecha_salida is not None:
        from .models import DelegacionCuenta
        DelegacionCuenta.objects.filter(miembro=miembro, revocada__isnull=True).update(revocada=timezone.now())
        EntidadMiembroRol.objects.filter(miembro=miembro, fecha_revocacion__isnull=True).update(fecha_revocacion=timezone.now())
        AsignacionRecurso.objects.filter(entidad_id=entidad_id, usuario=usuario,
            fecha_revocacion__isnull=True).update(fecha_revocacion=timezone.now())
        AsignacionFondo.objects.filter(fondo__entidad_id=entidad_id, usuario=usuario,
            fecha_revocacion__isnull=True).update(fecha_revocacion=timezone.now())
    miembro.fecha_salida = timezone.now() if retirar else None
    miembro.save(update_fields=["fecha_salida"])
    auditar(actor, "miembro.retirar" if retirar else "miembro.incorporar", "miembros", miembro.pk, entidad_id)
    return miembro


@transaction.atomic
def asignar_entidad(actor, entidad_id, miembro_id, rol_id, *, revocar=False):
    EntidadVerificable.objects.select_for_update().get(pk=entidad_id)
    exigir_responsable(actor, entidad_id)
    miembro = EntidadMiembro.objects.select_for_update().get(pk=miembro_id, entidad_id=entidad_id,
        fecha_salida__isnull=True, usuario__is_active=True)
    rol = Rol.objects.get(pk=rol_id, activo=True, ambito="ENTIDAD", delegable=True)
    if rol.codigo == "RESPONSABLE_PRINCIPAL":
        raise PermissionDenied("El cargo principal no es un nombramiento ordinario")
    asignacion, _ = EntidadMiembroRol.objects.get_or_create(miembro=miembro, rol=rol)
    asignacion.fecha_revocacion = timezone.now() if revocar else None
    asignacion.save(update_fields=["fecha_revocacion"])
    limpiar_asignaciones(miembro.usuario_id)
    auditar(actor, "rol_entidad.revocar" if revocar else "rol_entidad.asignar", "miembros", miembro.pk,
            entidad_id, rol_id=rol.pk)
    return asignacion


@transaction.atomic
def iniciar_transferencia(actor, entidad_id, sucesor_id, mantener_secundario=False):
    EntidadVerificable.objects.select_for_update().get(pk=entidad_id)
    exigir(actor, "principal.transferir", entidad_id=entidad_id)
    if not principal_de(actor, entidad_id):
        raise PermissionDenied("Solo el principal puede iniciar la transferencia")
    actual = ResponsableEntidad.objects.select_for_update().get(entidad_id=entidad_id)
    sucesor = EntidadMiembro.objects.get(pk=sucesor_id, entidad_id=entidad_id,
        fecha_salida__isnull=True, usuario__is_active=True)
    if actual.principal_id == sucesor.pk or not es_responsable(sucesor.usuario, entidad_id):
        raise ValidationError("El sucesor debe ser otro responsable vigente de la misma entidad")
    if TransferenciaResponsabilidad.objects.filter(entidad_id=entidad_id, estado="PENDIENTE").exists():
        raise ValidationError("Ya hay una transferencia pendiente")
    transferencia = TransferenciaResponsabilidad.objects.create(entidad_id=entidad_id,
        saliente=actual.principal, sucesor=sucesor, mantener_secundario=mantener_secundario)
    auditar(actor, "principal.transferencia_iniciar", "principal", transferencia.pk, entidad_id,
            mantener_secundario=mantener_secundario, sucesor_id=sucesor.pk)
    return transferencia


@transaction.atomic
def resolver_transferencia(actor, transferencia_id, *, aceptar):
    entidad_id = TransferenciaResponsabilidad.objects.get(pk=transferencia_id).entidad_id
    EntidadVerificable.objects.select_for_update().get(pk=entidad_id)
    transferencia = TransferenciaResponsabilidad.objects.select_for_update().select_related(
        "sucesor__usuario", "saliente__usuario").get(pk=transferencia_id)
    actual = ResponsableEntidad.objects.select_for_update().get(entidad_id=entidad_id)
    if transferencia.estado != "PENDIENTE" or actual.principal_id != transferencia.saliente_id:
        raise ValidationError("La transferencia ya no está pendiente")
    if not usuario_activo(actor):
        raise PermissionDenied("Cuenta inactiva")
    if aceptar:
        if actor.pk != transferencia.sucesor.usuario_id or not es_responsable(actor, entidad_id):
            raise PermissionDenied("Solo el sucesor que continúa autorizado puede aceptar")
        if not principal_de(transferencia.saliente.usuario_id, entidad_id):
            raise ValidationError("El principal saliente ya no está vigente; requiere recuperación")
        secundario = Rol.objects.get(codigo="RESPONSABLE_SECUNDARIO", activo=True)
        rol_salida, _ = EntidadMiembroRol.objects.get_or_create(miembro=transferencia.saliente, rol=secundario)
        rol_salida.fecha_revocacion = None if transferencia.mantener_secundario else timezone.now()
        rol_salida.save(update_fields=["fecha_revocacion"])
        actual.principal = transferencia.sucesor
        actual.save(update_fields=["principal"])
        transferencia.estado = "ACEPTADA"
    else:
        if actor.pk not in (transferencia.saliente.usuario_id, transferencia.sucesor.usuario_id):
            raise PermissionDenied("Solo las personas participantes pueden cancelar")
        transferencia.estado = "CANCELADA"
    transferencia.resuelta = timezone.now()
    transferencia.save(update_fields=["estado", "resuelta"])
    auditar(actor, "principal.transferencia_resolver", "principal", transferencia.pk, entidad_id,
            estado=transferencia.estado, mantener_secundario=transferencia.mantener_secundario)
    return transferencia


@transaction.atomic
def tomar(actor, recurso_codigo, objeto_id):
    if recurso_codigo == "fondo":
        raise ValidationError("Los fondos se asignan por sus responsables, no desde una cola")
    ctx = contexto(recurso_codigo, objeto_id, bloquear=True)
    exigir(actor, f"{recurso_codigo}.tomar", entidad_id=ctx.entidad_id)
    if not ctx.disponible:
        raise ValidationError("El registro ya no admite revisión")
    if recurso_codigo in ("adopcion", "verificacion") and ctx.propietario_id == actor.pk:
        raise PermissionDenied("No puedes revisar tu propia solicitud")
    if recurso_codigo != "verificacion" and not EntidadVerificable.objects.filter(
        pk=ctx.entidad_id, estado_verificacion__tipo__nombre="estado_verificacion",
        estado_verificacion__nombre="Verificada").exists():
        raise ValidationError("La entidad no está verificada")
    from core.models import Recurso
    recurso = Recurso.objects.get(codigo=recurso_codigo, activo=True)
    asignacion = AsignacionRecurso.objects.select_for_update().filter(recurso=recurso, objeto_id=objeto_id).first()
    if asignacion and asignacion.fecha_revocacion is None:
        raise ValidationError("El registro ya tiene una asignación vigente")
    asignacion, _ = AsignacionRecurso.objects.update_or_create(recurso=recurso, objeto_id=objeto_id,
        defaults={"usuario": actor, "entidad_id": ctx.entidad_id, "fecha_revocacion": None})
    auditar(actor, "revision.tomar", recurso_codigo, objeto_id, ctx.entidad_id)
    return asignacion


@transaction.atomic
def devolver(actor, recurso_codigo, objeto_id, motivo):
    if recurso_codigo == "fondo":
        raise ValidationError("El retiro de fondos corresponde a sus responsables")
    motivo = motivo_obligatorio(motivo)
    ctx = contexto(recurso_codigo, objeto_id, bloquear=True)
    exigir(actor, f"{recurso_codigo}.ver", entidad_id=ctx.entidad_id, objeto_id=objeto_id)
    if not ctx.disponible:
        raise ValidationError("El registro ya no admite devolución")
    asignacion = AsignacionRecurso.objects.select_for_update().get(recurso__codigo=recurso_codigo,
        objeto_id=objeto_id, usuario=actor, fecha_revocacion__isnull=True)
    asignacion.fecha_revocacion = timezone.now()
    asignacion.save(update_fields=["fecha_revocacion"])
    auditar(actor, "revision.devolver", recurso_codigo, objeto_id, ctx.entidad_id, motivo)
    return asignacion


@transaction.atomic
def asignar_fondo(actor, fondo_id, miembro_id, *, revocar=False):
    ctx = contexto("fondo", fondo_id, bloquear=True)
    exigir_responsable(actor, ctx.entidad_id)
    exigir(actor, "fondo.asignar", entidad_id=ctx.entidad_id)
    miembro = EntidadMiembro.objects.get(pk=miembro_id, entidad_id=ctx.entidad_id,
        fecha_salida__isnull=True, usuario__is_active=True)
    if not tiene_base(miembro.usuario, "fondo.reportar_distribucion", entidad_id=ctx.entidad_id):
        raise ValidationError("La persona no tiene el rol operativo para este fondo")
    asignacion = AsignacionFondo.objects.select_for_update().filter(fondo_id=fondo_id, usuario_id=miembro.usuario_id).first()
    if revocar and asignacion is None:
        raise ValidationError("No existe esa asignación")
    asignacion, _ = AsignacionFondo.objects.update_or_create(fondo_id=fondo_id, usuario=miembro.usuario,
        defaults={"fecha_revocacion": timezone.now() if revocar else None})
    auditar(actor, "fondo.retirar" if revocar else "fondo.asignar", "fondo", fondo_id,
            ctx.entidad_id, usuario_id=miembro.usuario_id)
    return asignacion

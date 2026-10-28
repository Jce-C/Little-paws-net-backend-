"""Autorización actual consultada en BD: sin bypass de superusuario ni JWT de roles."""
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from accounts.models import Usuario
from core.models import EntidadMiembro, EntidadMiembroRol, Permiso, RolPermiso, UsuarioRol
from .models import AsignacionFondo, AsignacionRecurso, ResponsableEntidad
from .objetos import contexto
from .politicas import POLITICAS


def usuario_activo(usuario):
    pk = getattr(usuario, "pk", usuario)
    return bool(pk and Usuario.objects.filter(pk=pk, is_active=True).exists())


def principal_de(usuario, entidad_id):
    pk = getattr(usuario, "pk", usuario)
    return usuario_activo(pk) and ResponsableEntidad.objects.filter(
        entidad_id=entidad_id, principal__entidad_id=entidad_id,
        principal__usuario_id=pk, principal__usuario__is_active=True,
        principal__fecha_salida__isnull=True,
    ).exists()


def permiso_vigente(codigo):
    politica = POLITICAS.get(codigo)
    if politica is None:
        return None
    recurso, accion, alcance = politica
    return Permiso.objects.filter(codigo=codigo, activo=True, recurso__activo=True,
                                   recurso__codigo=recurso, accion=accion, alcance=alcance).first()


def tiene_base(usuario, codigo, *, entidad_id=None):
    """Tener un rol NO prueba asignación, custodia ni autorización del expediente."""
    pk = getattr(usuario, "pk", usuario)
    if not usuario_activo(pk):
        return False
    permiso = permiso_vigente(codigo)
    if permiso is None:
        return False
    es_global = permiso.alcance == Permiso.Alcance.GLOBAL or permiso.recurso.codigo in ("verificacion", "reclamacion")
    if es_global:
        return UsuarioRol.objects.filter(usuario_id=pk, fecha_revocacion__isnull=True,
            rol__activo=True, rol__ambito="GLOBAL", rol__rolpermiso__permiso=permiso).exists()
    if entidad_id is None:
        return False
    if not EntidadMiembro.objects.filter(entidad_id=entidad_id, usuario_id=pk,
                                        fecha_salida__isnull=True).exists():
        return False
    # Un principal se representa en la fila única, no mediante un rol asignable.
    if principal_de(pk, entidad_id) and RolPermiso.objects.filter(
        rol__codigo="RESPONSABLE_PRINCIPAL", rol__activo=True, permiso=permiso).exists():
        return True
    return EntidadMiembroRol.objects.filter(miembro__usuario_id=pk,
        miembro__entidad_id=entidad_id, miembro__fecha_salida__isnull=True,
        fecha_revocacion__isnull=True, rol__activo=True, rol__ambito="ENTIDAD",
        rol__rolpermiso__permiso=permiso).exclude(rol__codigo="RESPONSABLE_PRINCIPAL").exists()


def puede(usuario, codigo, *, entidad_id=None, objeto_id=None):
    permiso = permiso_vigente(codigo)
    if permiso is None:
        return False
    if permiso.alcance == Permiso.Alcance.ASIGNADO:
        if objeto_id is None:
            return False
        if permiso.recurso.codigo == "reclamacion":
            from .models import ReclamacionMascota
            return tiene_base(usuario, codigo) and ReclamacionMascota.objects.filter(
                pk=objeto_id, revisor_id=getattr(usuario, "pk", usuario)).exclude(
                reclamante_id=getattr(usuario, "pk", usuario)).exclude(
                mascota__dueno_id=getattr(usuario, "pk", usuario)).exists()
        from rest_framework.exceptions import APIException
        try:
            ctx = contexto(permiso.recurso.codigo, objeto_id)
        except APIException:
            return False
        if ctx.entidad_id is None or (entidad_id is not None and ctx.entidad_id != entidad_id):
            return False
        if not tiene_base(usuario, codigo, entidad_id=ctx.entidad_id):
            return False
        pk = getattr(usuario, "pk", usuario)
        if permiso.recurso.codigo == "fondo":
            return AsignacionFondo.objects.filter(fondo_id=objeto_id, fondo__entidad_id=ctx.entidad_id,
                usuario_id=pk, fecha_revocacion__isnull=True).exists()
        return AsignacionRecurso.objects.filter(recurso=permiso.recurso, objeto_id=objeto_id,
            entidad_id=ctx.entidad_id, usuario_id=pk, fecha_revocacion__isnull=True).exists()
    if permiso.alcance == Permiso.Alcance.AUTORIZADO:
        if codigo == "cuenta.preparar":
            from .models import DelegacionCuenta
            pk = getattr(usuario, "pk", usuario)
            return usuario_activo(pk) and entidad_id is not None and not principal_de(pk, entidad_id) and DelegacionCuenta.objects.filter(
                entidad_id=entidad_id, miembro__usuario_id=pk,
                miembro__fecha_salida__isnull=True, revocada__isnull=True).exists()
        if objeto_id is None or not usuario_activo(usuario):
            return False
        from core.models import Veterinario
        from animals.models import AutorizacionExpediente
        pk = getattr(usuario, "pk", usuario)
        vet = Veterinario.objects.filter(usuario_profesional_id=pk,
            entidad__estado_verificacion__tipo__nombre="estado_verificacion",
            entidad__estado_verificacion__nombre="Verificada").first()
        if vet is None or not tiene_base(pk, codigo, entidad_id=vet.entidad_id):
            return False
        return AutorizacionExpediente.objects.filter(mascota_id=objeto_id, veterinario=vet,
            fecha_revocacion__isnull=True, fecha_expiracion__gt=timezone.now()).exists()
    if permiso.alcance == Permiso.Alcance.PROPIO:
        # No conceder alcances propios genéricos sin resolver la titularidad real.
        return False
    return tiene_base(usuario, codigo, entidad_id=entidad_id)


def exigir(usuario, codigo, **context):
    if not puede(usuario, codigo, **context):
        raise PermissionDenied("No tienes permiso para esta operación en ese ámbito")

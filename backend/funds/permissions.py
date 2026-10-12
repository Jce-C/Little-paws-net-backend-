"""Comprobaciones RBAC independientes de is_staff y del superusuario de Django."""

from core.models import EntidadMiembroRol, Rol, UsuarioRol


def administrador_puede(usuario, codigo_permiso):
    return bool(
        usuario.is_authenticated
        and usuario.is_active
        and UsuarioRol.objects.filter(
            usuario=usuario,
            fecha_revocacion__isnull=True,
            rol__codigo="ADMIN_PLATAFORMA",
            rol__ambito=Rol.Ambito.GLOBAL,
            rol__rolpermiso__permiso__codigo=codigo_permiso,
        ).exists()
    )


def gestor_fundacion_puede(usuario, fundacion_id, codigo_permiso):
    return bool(
        usuario.is_authenticated
        and usuario.is_active
        and EntidadMiembroRol.objects.filter(
            miembro__entidad_id=fundacion_id,
            miembro__usuario=usuario,
            miembro__fecha_salida__isnull=True,
            rol__codigo="GESTOR_FUNDACION",
            rol__ambito=Rol.Ambito.ENTIDAD,
            rol__rolpermiso__permiso__codigo=codigo_permiso,
        ).exists()
    )

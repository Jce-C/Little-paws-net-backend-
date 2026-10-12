"""Comprobaciones RBAC independientes de is_staff y del superusuario de Django."""

from core.models import Rol, UsuarioRol


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

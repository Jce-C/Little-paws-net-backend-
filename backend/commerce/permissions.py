"""RBAC comercial: los permisos de tienda se limitan a su entidad."""

from core.models import EntidadMiembroRol, Rol, UsuarioRol


def administrador_puede(usuario, codigo_permiso):
    return bool(
        usuario.is_authenticated and usuario.is_active
        and UsuarioRol.objects.filter(
            usuario=usuario, fecha_revocacion__isnull=True,
            rol__codigo="ADMIN_PLATAFORMA", rol__ambito=Rol.Ambito.GLOBAL,
            rol__rolpermiso__permiso__codigo=codigo_permiso,
        ).exists()
    )


def gestor_tienda_puede(usuario, tienda_id, codigo_permiso):
    return bool(
        usuario.is_authenticated and usuario.is_active
        and EntidadMiembroRol.objects.filter(
            miembro__entidad_id=tienda_id, miembro__usuario=usuario,
            miembro__fecha_salida__isnull=True,
            rol__codigo="GESTOR_TIENDA", rol__ambito=Rol.Ambito.ENTIDAD,
            rol__rolpermiso__permiso__codigo=codigo_permiso,
        ).exists()
    )


def gestor_anunciante_puede(usuario, anunciante_id, codigo_permiso):
    return bool(
        usuario.is_authenticated and usuario.is_active
        and EntidadMiembroRol.objects.filter(
            miembro__entidad_id=anunciante_id, miembro__usuario=usuario,
            miembro__fecha_salida__isnull=True,
            rol__codigo="GESTOR_ANUNCIANTE", rol__ambito=Rol.Ambito.ENTIDAD,
            rol__rolpermiso__permiso__codigo=codigo_permiso,
        ).exists()
    )

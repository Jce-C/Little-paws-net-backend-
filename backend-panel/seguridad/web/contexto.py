"""Navegación derivada de permisos actuales, nunca de una selección del navegador."""
from core.models import EntidadMiembro, UsuarioRol, Rol
from seguridad.autorizacion import tiene_base, puede, principal_de
from seguridad.models import AsignacionRecurso, ResponsableEntidad


MODULOS = [
    ("usuarios", "Usuarios", "Seguridad", "usuarios.ver", "GLOBAL", "Personas y estado de sus cuentas"),
    ("roles", "Roles y permisos", "Seguridad", "roles.ver", "GLOBAL", "Responsabilidades y acciones permitidas"),
    ("recursos", "Recursos", "Seguridad", "recursos.ver", "GLOBAL", "Módulos protegidos de la plataforma"),
    ("permisos", "Permisos", "Seguridad", "permisos.ver", "GLOBAL", "Acciones reconocidas y su alcance"),
    ("auditoria", "Auditoría", "Seguridad", "auditoria.ver", "GLOBAL", "Registro de acciones administrativas"),
    ("verificaciones", "Verificaciones", "Moderación", "verificacion.tomar", "GLOBAL", "Solicitudes disponibles para revisión"),
    ("reclamaciones", "Reclamaciones", "Moderación", "reclamacion.tomar", "GLOBAL", "Revisión de titularidad en dos pasos"),
    ("revision-publicidad", "Revisión de anuncios", "Moderación", "publicidad.revisar", "GLOBAL", "Contenido pendiente de aprobación"),
    ("equipo", "Equipo y responsables", "Mi organización", "miembros.ver", "ENTIDAD", "Integrantes y responsabilidades de tu entidad"),
    ("cuentas", "Cuentas receptoras", "Mi organización", "cuenta.aprobar", "ENTIDAD", "Propuestas y aprobación de cambios"),
    ("rescates", "Casos de rescate", "Operación", "caso.ver", "ENTIDAD", "Casos de tu fundación"),
    ("adopciones", "Adopciones", "Operación", "adopcion.tomar", "ENTIDAD", "Solicitudes pendientes de asignación"),
    ("aportes", "Aportes", "Operación", "aporte.tomar", "ENTIDAD", "Revisiones disponibles, sin ejecutar pagos"),
    ("pedidos", "Pedidos", "Operación", "pedido.tomar", "ENTIDAD", "Trabajo disponible de tu tienda"),
    ("catalogo", "Catálogo", "Operación", "producto.gestionar", "ENTIDAD", "Productos, precios y disponibilidad"),
    ("fondos", "Fondos asignados", "Operación", "fondo.ver", "ENTIDAD", "Fondos en los que puedes trabajar"),
    ("publicidad", "Publicidad", "Operación", "publicidad.gestionar", "ENTIDAD", "Anuncios y versiones de tu entidad"),
    ("expedientes", "Expedientes autorizados", "Atención veterinaria", "expediente.escribir", "ENTIDAD", "Mascotas con autorización vigente"),
]

# Presentación: estos identificadores solo seleccionan colores e iconos.
# No participan en tiene_base(), puede() ni en el alcance de los recursos.
ICONOS = dict(zip(
    (m[0] for m in MODULOS),
    ("users", "shield-check", "boxes", "key-round", "history", "clipboard-check",
     "scale", "megaphone", "building-2", "landmark", "paw-print", "heart-handshake",
     "hand-coins", "shopping-bag", "package", "chart-no-axes-combined", "megaphone", "stethoscope"),
))
PERFILES_VISUALES = {
    "ADMIN_SEGURIDAD": ("admin_seguridad", "Administrador de seguridad"),
    "MODERADOR": ("moderador", "Moderador de plataforma"),
    "RESPONSABLE_PRINCIPAL": ("responsable_principal", "Responsable principal"),
    "RESPONSABLE_SECUNDARIO": ("responsable_secundario", "Responsable secundario"),
    "GESTOR_RESCATES": ("gestor_rescates", "Gestor de rescates"),
    "GESTOR_ADOPCIONES": ("gestor_adopciones", "Gestor de adopciones"),
    "GESTOR_APORTES": ("gestor_aportes", "Gestor de aportes"),
    "GESTOR_CATALOGO": ("gestor_catalogo", "Gestor de catálogo"),
    "GESTOR_PEDIDOS": ("gestor_pedidos", "Gestor de pedidos"),
    "GESTOR_FONDO": ("gestor_fondo", "Gestor de fondo"),
    "GESTOR_PUBLICIDAD": ("gestor_publicidad", "Gestor de publicidad"),
    "VETERINARIO": ("veterinario", "Veterinario verificado"),
}


def perfil_visual(codigos, preparador=False):
    """Prioridad visual estable para cuentas con varios roles simultáneos."""
    for codigo, perfil in PERFILES_VISUALES.items():
        if codigo in codigos:
            return perfil
    if preparador:
        return "preparador_cuentas", "Preparador delegado de cuentas"
    return "", "Equipo autorizado"


def construir(request):
    usuario = request.user
    organizaciones = []
    for miembro in EntidadMiembro.objects.filter(usuario=usuario, fecha_salida__isnull=True).select_related("entidad"):
        codigos = list(miembro.entidadmiembrorol_set.filter(fecha_revocacion__isnull=True,
            rol__activo=True, rol__ambito="ENTIDAD").exclude(rol__codigo="RESPONSABLE_PRINCIPAL").values_list("rol__codigo", flat=True))
        if principal_de(usuario, miembro.entidad_id):
            codigos.append("RESPONSABLE_PRINCIPAL")
        if codigos or puede(usuario, "cuenta.preparar", entidad_id=miembro.entidad_id):
            organizaciones.append({"id": miembro.entidad_id, "nombre": miembro.entidad.nombre, "roles": codigos})
    seleccion = next((e for e in organizaciones if e["id"] == request.session.get("lpn_entidad")),
                     organizaciones[0] if organizaciones else None)
    entidad_id = seleccion["id"] if seleccion else None
    modulos = []
    for codigo, nombre, grupo, permiso, ambito, descripcion in MODULOS:
        autorizado = tiene_base(usuario, permiso, entidad_id=entidad_id if ambito == "ENTIDAD" else None)
        if codigo == "cuentas":
            autorizado = autorizado or puede(usuario, "cuenta.preparar", entidad_id=entidad_id)
        if autorizado:
            modulos.append({"codigo": codigo, "nombre": nombre, "grupo": grupo, "descripcion": descripcion, "icono": ICONOS[codigo]})
    roles_globales = list(UsuarioRol.objects.filter(usuario=usuario, fecha_revocacion__isnull=True,
        rol__activo=True, rol__ambito="GLOBAL").exclude(rol__codigo="CIUDADANO").values_list("rol__codigo", "rol__nombre"))
    globales = [nombre for _, nombre in roles_globales]
    tema, etiqueta = perfil_visual([codigo for codigo, _ in roles_globales] + (seleccion["roles"] if seleccion else []),
        preparador=any(m["codigo"] == "cuentas" for m in modulos))
    return {"organizaciones": organizaciones, "seleccion": seleccion, "entidad_id": entidad_id,
        "modulos": modulos, "globales": globales, "puede_panel": bool(modulos),
        "perfil_visual": tema, "rol_visible": etiqueta}

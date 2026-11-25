"""Operaciones reconocidas por el servidor; el catálogo no crea endpoints."""

RECURSOS = {
    "mascotas": "Mascotas", "reportes": "Reportes de rescate", "configuracion": "Configuración de la plataforma", "usuarios": "Usuarios", "roles": "Roles", "recursos": "Recursos",
    "permisos": "Permisos", "entidades": "Entidades", "miembros": "Integrantes",
    "principal": "Responsabilidad principal", "auditoria": "Auditoría de seguridad",
    "caso": "Casos de rescate", "adopcion": "Solicitudes de adopción",
    "aporte": "Revisiones de aportes", "pedido": "Pedidos", "fondo": "Fondos externos",
    "producto": "Catálogo de productos", "publicidad": "Publicidad",
    "reporte": "Reportes", "verificacion": "Verificación de entidades",
    "expediente": "Expedientes médicos", "cuenta": "Cuentas receptoras",
    "reclamacion": "Reclamaciones de titularidad",
}

# código -> (recurso, acción, alcance). Los alcances no son editables por el cliente.
POLITICAS = {}
for recurso in ("usuarios", "roles", "recursos", "permisos"):
    for accion in ("ver", "crear", "editar"):
        POLITICAS[f"{recurso}.{accion}"] = (recurso, accion, "GLOBAL")
for codigo, recurso, accion in (
    ("roles.asignar", "roles", "asignar"),
    ("entidades.ver", "entidades", "ver"),
    ("principal.designar", "principal", "designar"),
    ("auditoria.ver", "auditoria", "ver"),
):
    POLITICAS[codigo] = (recurso, accion, "GLOBAL")
for codigo, recurso, accion in (
    ("miembros.ver", "miembros", "ver"), ("miembros.gestionar", "miembros", "gestionar"),
    ("miembros.roles", "miembros", "roles"), ("principal.transferir", "principal", "transferir"),
    ("caso.ver", "caso", "ver"), ("caso.aceptar", "caso", "aceptar"),
    ("caso.cambiar_estado", "caso", "cambiar_estado"),
    ("producto.gestionar", "producto", "gestionar"),
    ("publicidad.gestionar", "publicidad", "gestionar"),
    ("fondo.solicitar", "fondo", "solicitar"), ("fondo.asignar", "fondo", "asignar"),
    ("expediente.autorizar", "expediente", "autorizar"),
):
    POLITICAS[codigo] = (recurso, accion, "ENTIDAD")
for recurso, acciones in {
    "adopcion": ("ver", "resolver"), "aporte": ("ver", "confirmar"),
    "pedido": ("ver", "gestionar"), "fondo": ("ver", "reportar_distribucion"),
    "verificacion": ("ver",),
}.items():
    for accion in acciones:
        POLITICAS[f"{recurso}.{accion}"] = (recurso, accion, "ASIGNADO")
for recurso in ("adopcion", "aporte", "pedido"):
    POLITICAS[f"{recurso}.tomar"] = (recurso, "tomar", "ENTIDAD")
POLITICAS.update({
    "cuenta.delegar": ("cuenta", "delegar", "ENTIDAD"),
    "cuenta.aprobar": ("cuenta", "aprobar", "ENTIDAD"),
    "cuenta.preparar": ("cuenta", "preparar", "AUTORIZADO"),
    "reclamacion.tomar": ("reclamacion", "tomar", "GLOBAL"),
    "reclamacion.resolver": ("reclamacion", "resolver", "ASIGNADO"),
    "reclamacion.ejecutar": ("reclamacion", "ejecutar", "ASIGNADO"),
    "verificacion.tomar": ("verificacion", "tomar", "GLOBAL"),
    "entidad.validar": ("verificacion", "validar", "ASIGNADO"),
    "publicidad.revisar": ("publicidad", "revisar", "GLOBAL"),
    "reporte.moderar": ("reporte", "moderar", "GLOBAL"),
    "expediente.escribir": ("expediente", "escribir", "AUTORIZADO"),
})

POLITICAS.update({"configuracion.ver": ("configuracion", "ver", "GLOBAL"), "configuracion.editar": ("configuracion", "editar", "GLOBAL")})

POLITICAS.update({
    "entidades.crear": ("entidades","crear","GLOBAL"), "entidades.editar": ("entidades","editar","GLOBAL"),
    "mascotas.ver": ("mascotas","ver","GLOBAL"), "mascotas.crear": ("mascotas","crear","GLOBAL"), "mascotas.editar": ("mascotas","editar","GLOBAL"),
    "reportes.ver": ("reportes","ver","GLOBAL"), "fondo.crear": ("fondo","crear","GLOBAL"), "fondo.editar": ("fondo","editar","GLOBAL"), "adopcion.seguimiento": ("adopcion","seguimiento","ASIGNADO"),
})
POLITICAS.update({'mascotas.participar': ('mascotas', 'participar', 'GLOBAL'), 'reportes.participar': ('reportes', 'participar', 'GLOBAL'), 'adopcion.participar': ('adopcion', 'participar', 'GLOBAL'), 'aporte.participar': ('aporte', 'participar', 'GLOBAL'), 'pedido.participar': ('pedido', 'participar', 'GLOBAL'), 'fondo.participar': ('fondo', 'participar', 'GLOBAL'), 'producto.consultar': ('producto', 'consultar', 'GLOBAL'), 'reclamacion.presentar': ('reclamacion', 'presentar', 'GLOBAL')})
POLITICAS.update({'comunidad.participar': ('comunidad', 'participar', 'GLOBAL'),
                  'comunidad.moderar': ('comunidad', 'moderar', 'GLOBAL'),
                  'ayudas.participar': ('ayudas', 'participar', 'GLOBAL')})
POLITICAS['ayudas.gestionar'] = ('ayudas', 'gestionar', 'ENTIDAD')
SEGURIDAD = tuple(c for c, (_, _, alcance) in POLITICAS.items()
                  if alcance == "GLOBAL" and not c.startswith(("verificacion.", "publicidad.", "reporte.", "reclamacion.")))
EQUIPO = ("miembros.ver", "miembros.gestionar", "miembros.roles", "fondo.asignar", "ayudas.gestionar")
# código -> (nombre, ámbito, delegable, permisos)
ROLES = {
    "ADMIN_SEGURIDAD": ("Administrador de seguridad", "GLOBAL", False, SEGURIDAD),
    "MODERADOR": ("Moderador de plataforma", "GLOBAL", False,
                  ("verificacion.tomar", "verificacion.ver", "entidad.validar", "publicidad.revisar", "reporte.moderar",
                   "reclamacion.tomar", "reclamacion.resolver", "reclamacion.ejecutar", "comunidad.moderar")),
    "CIUDADANO": ("Ciudadano", "GLOBAL", False, ('mascotas.participar', 'reportes.participar', 'adopcion.participar', 'aporte.participar', 'pedido.participar', 'fondo.participar', 'producto.consultar', 'reclamacion.presentar','cuenta.preparar','comunidad.participar','ayudas.participar')),
    "RESPONSABLE_PRINCIPAL": ("Responsable principal", "ENTIDAD", False,
                               EQUIPO + ("principal.transferir", "cuenta.delegar", "cuenta.aprobar", "expediente.autorizar")),
    "RESPONSABLE_SECUNDARIO": ("Responsable secundario", "ENTIDAD", True, EQUIPO),
    "GESTOR_RESCATES": ("Gestor de rescates", "ENTIDAD", True,
                        ("caso.ver", "caso.aceptar", "caso.cambiar_estado")),
    "GESTOR_ADOPCIONES": ("Gestor de adopciones", "ENTIDAD", True,
                          ("adopcion.tomar", "adopcion.ver", "adopcion.resolver", "adopcion.seguimiento")),
    "GESTOR_APORTES": ("Gestor de aportes", "ENTIDAD", True,
                       ("aporte.tomar", "aporte.ver", "aporte.confirmar")),
    "GESTOR_CATALOGO": ("Gestor de catálogo", "ENTIDAD", True, ("producto.gestionar",)),
    "GESTOR_PEDIDOS": ("Gestor de pedidos", "ENTIDAD", True, ("pedido.tomar", "pedido.ver", "pedido.gestionar")),
    "GESTOR_FONDO": ("Gestor de fondo", "ENTIDAD", True, ("fondo.ver", "fondo.reportar_distribucion")),
    "GESTOR_PUBLICIDAD": ("Gestor de publicidad", "ENTIDAD", True, ("publicidad.gestionar",)),
    "VETERINARIO": ("Veterinario verificado", "ENTIDAD", True, ("expediente.escribir",)),
}

LEGADOS = ("ADMIN_PLATAFORMA", "GESTOR_FUNDACION", "GESTOR_TIENDA")

# Administrative actions have real handlers; arbitrary strings never authorize endpoints.
for recurso in ('usuarios','roles','entidades'):
    for accion in ('eliminar','desactivar','restaurar'):
        POLITICAS[f'{recurso}.{accion}']=(recurso,accion,'GLOBAL')
POLITICAS['auditoria.exportar']=('auditoria','exportar','GLOBAL')

RECURSOS["catalogos"]="Catálogos del sistema"
for accion in ("ver","crear","editar"):POLITICAS["catalogos."+accion]=("catalogos",accion,"GLOBAL")
POLITICAS["caso.cobertura"]=("caso","cobertura","ENTIDAD")

POLITICAS["caso.registrar_mascota"]=("caso","registrar_mascota","ENTIDAD")
POLITICAS["mascotas.publicar_adopcion"]=("mascotas","publicar_adopcion","ENTIDAD")

POLITICAS["producto.eliminar"]=("producto","eliminar","ENTIDAD")

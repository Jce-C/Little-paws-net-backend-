"""Datos de referencia de apadrinamiento, adopción, fondo y comercio."""

from django.db import migrations


CATALOGOS = {
    "estado_apadrinamiento": ("En espera", "Aceptado", "Rechazado", "Cancelado"),
    "estado_adopcion": ("Pendiente", "Aprobada", "Rechazada", "Cerrada por adopción"),
    "tipo_documento": ("Historia clínica", "Identificación", "Vacunación"),
    "tipo_fondo": ("Emergencias", "General"),
    "estado_fondo": ("Activo", "Inactivo"),
    "estado_donacion": ("Comprometida", "Reportada", "Cancelada"),
    "estado_distribucion": ("Reportada", "Recepción confirmada por fundación"),
    "estado_emergencia": ("Pendiente", "Atendida", "Rechazada"),
    "categoria_producto": ("Alimentos", "Accesorios", "Salud"),
    "tipo_producto": ("Alimento seco", "Collar", "Medicamento"),
    "estado_producto": ("Disponible", "Inactivo"),
    "estado_pedido": ("Iniciado", "Contactado", "Cancelado"),
    "tipo_publicidad": ("Banner", "Destacado"),
    "estado_publicidad": ("Pendiente", "Aprobada", "Rechazada"),
    "nivel_alianza": ("Básica", "Premium"),
    "estado_alianza": ("Activa", "Inactiva"),
    "tipo_tarifa": ("Publicación", "Promoción"),
    "resultado_moderacion": ("Aprobado", "Rechazado"),
    "tipo_notificacion": ("Caso aceptado", "Resultado de adopción", "Pedido iniciado"),
}

PERMISOS = {
    "aporte.confirmar": "Confirmar recepción de un aporte por la fundación",
    "adopcion.resolver": "Resolver solicitudes de adopción bajo custodia",
    "fondo.solicitar": "Solicitar ayuda de un fondo externo",
    "fondo.reportar_distribucion": "Registrar distribución informativa del fondo",
    "producto.gestionar": "Administrar catálogo de una tienda",
    "pedido.gestionar": "Gestionar pedidos iniciados de una tienda",
    "publicidad.revisar": "Aprobar o rechazar publicidad",
    "entidad.validar": "Resolver una solicitud de validación",
    "reporte.moderar": "Moderar reportes ciudadanos",
}

ROLES_ENTIDAD = {
    "GESTOR_FUNDACION": ("aporte.confirmar", "adopcion.resolver", "fondo.solicitar"),
    "GESTOR_FONDO": ("fondo.reportar_distribucion",),
    "GESTOR_TIENDA": ("producto.gestionar", "pedido.gestionar"),
}


def crear_catalogos(apps, schema_editor):
    TipoMaestro = apps.get_model("core", "TipoMaestro")
    ValorMaestro = apps.get_model("core", "ValorMaestro")
    Rol = apps.get_model("core", "Rol")
    Permiso = apps.get_model("core", "Permiso")
    RolPermiso = apps.get_model("core", "RolPermiso")
    alias = schema_editor.connection.alias

    for nombre_tipo, valores in CATALOGOS.items():
        tipo, _ = TipoMaestro.objects.using(alias).get_or_create(
            nombre=nombre_tipo, defaults={"descripcion": nombre_tipo.replace("_", " ")}
        )
        for nombre_valor in valores:
            ValorMaestro.objects.using(alias).get_or_create(tipo=tipo, nombre=nombre_valor)

    permisos = {}
    for codigo, descripcion in PERMISOS.items():
        permiso, _ = Permiso.objects.using(alias).get_or_create(
            codigo=codigo, defaults={"descripcion": descripcion}
        )
        permisos[codigo] = permiso

    admin = Rol.objects.using(alias).get(codigo="ADMIN_PLATAFORMA")
    for permiso in permisos.values():
        RolPermiso.objects.using(alias).get_or_create(rol=admin, permiso=permiso)
    for codigo, codigos_permiso in ROLES_ENTIDAD.items():
        rol, _ = Rol.objects.using(alias).get_or_create(
            codigo=codigo,
            defaults={"nombre": codigo.replace("_", " ").title(), "ambito": "ENTIDAD"},
        )
        for codigo_permiso in codigos_permiso:
            RolPermiso.objects.using(alias).get_or_create(
                rol=rol, permiso=permisos[codigo_permiso]
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0005_notificacion")]

    operations = [migrations.RunPython(crear_catalogos, migrations.RunPython.noop)]

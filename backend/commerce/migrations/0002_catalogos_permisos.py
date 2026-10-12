"""Catálogos y permisos mínimos del proceso comercial."""

from django.db import migrations


CATALOGOS = {
    "categoria_producto": ("Alimentos", "Accesorios", "Salud"),
    "tipo_producto": ("Alimento seco", "Collar", "Otro"),
    "estado_producto": ("Disponible", "Inactivo"),
    "estado_pedido": ("Iniciado", "Cancelado"),
    "tipo_publicidad": ("Banner",),
    "tipo_tarifa": ("Mensual",),
    "tipo_notificacion": ("Pedido iniciado",),
}

PERMISOS = {
    "producto.gestionar": "Crear y mantener productos de una tienda propia",
    "pedido.consultar_tienda": "Consultar pedidos iniciados para una tienda propia",
    "publicidad.gestionar": "Administrar espacios publicitarios del anunciante propio",
    "tarifa.gestionar": "Administrar tarifas de publicación",
}

ROLES = {
    "GESTOR_TIENDA": ("Gestor de tienda", "ENTIDAD", ("producto.gestionar", "pedido.consultar_tienda")),
    "GESTOR_ANUNCIANTE": ("Gestor de anunciante", "ENTIDAD", ("publicidad.gestionar",)),
}


def cargar(apps, schema_editor):
    Tipo = apps.get_model("core", "TipoMaestro")
    Valor = apps.get_model("core", "ValorMaestro")
    Rol = apps.get_model("core", "Rol")
    Permiso = apps.get_model("core", "Permiso")
    RolPermiso = apps.get_model("core", "RolPermiso")
    alias = schema_editor.connection.alias

    for nombre_tipo, nombres in CATALOGOS.items():
        tipo, _ = Tipo.objects.using(alias).get_or_create(
            nombre=nombre_tipo,
            defaults={"descripcion": nombre_tipo.replace("_", " ")},
        )
        for nombre in nombres:
            Valor.objects.using(alias).get_or_create(tipo=tipo, nombre=nombre)

    permisos = {}
    for codigo, descripcion in PERMISOS.items():
        permiso, _ = Permiso.objects.using(alias).get_or_create(
            codigo=codigo, defaults={"descripcion": descripcion},
        )
        permisos[codigo] = permiso

    for codigo, (nombre, ambito, codigos) in ROLES.items():
        rol, _ = Rol.objects.using(alias).get_or_create(
            codigo=codigo, defaults={"nombre": nombre, "ambito": ambito},
        )
        for codigo_permiso in codigos:
            RolPermiso.objects.using(alias).get_or_create(rol=rol, permiso=permisos[codigo_permiso])

    administrador = Rol.objects.using(alias).get(codigo="ADMIN_PLATAFORMA")
    for permiso in permisos.values():
        RolPermiso.objects.using(alias).get_or_create(rol=administrador, permiso=permiso)


class Migration(migrations.Migration):
    dependencies = [("commerce", "0001_initial")]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]

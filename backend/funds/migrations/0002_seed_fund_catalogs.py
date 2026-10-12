"""Estados y permisos explícitos para el fondo externo."""

from django.db import migrations


ESTADOS = {
    "estado_donacion": ("Comprometida", "Confirmada", "Rechazada", "Cancelada"),
    "estado_distribucion": ("Reportada", "Confirmada", "Rechazada"),
}

PERMISOS = {
    "fondo.gestionar": "Configurar fondos externos y sus instrucciones protegidas",
    "donacion.confirmar": "Registrar una confirmación documentada de donación",
    "distribucion.reportar": "Registrar una distribución informada por el fondo externo",
    "distribucion.confirmar": "Confirmar recepción para la fundación destinataria",
}

ROLES = {
    "ADMIN_PLATAFORMA": (
        "fondo.gestionar", "donacion.confirmar", "distribucion.reportar",
    ),
    "GESTOR_FUNDACION": ("distribucion.confirmar",),
}


def cargar(apps, schema_editor):
    Tipo = apps.get_model("core", "TipoMaestro")
    Valor = apps.get_model("core", "ValorMaestro")
    Permiso = apps.get_model("core", "Permiso")
    Rol = apps.get_model("core", "Rol")
    RolPermiso = apps.get_model("core", "RolPermiso")
    alias = schema_editor.connection.alias

    for nombre_tipo, valores in ESTADOS.items():
        tipo, _ = Tipo.objects.using(alias).get_or_create(
            nombre=nombre_tipo,
            defaults={"descripcion": nombre_tipo.replace("_", " ")},
        )
        for nombre in valores:
            Valor.objects.using(alias).get_or_create(tipo=tipo, nombre=nombre)

    permisos = {}
    for codigo, descripcion in PERMISOS.items():
        permiso, _ = Permiso.objects.using(alias).get_or_create(
            codigo=codigo, defaults={"descripcion": descripcion},
        )
        permisos[codigo] = permiso

    for codigo_rol, codigos_permiso in ROLES.items():
        rol = Rol.objects.using(alias).get(codigo=codigo_rol)
        for codigo_permiso in codigos_permiso:
            RolPermiso.objects.using(alias).get_or_create(
                rol=rol, permiso=permisos[codigo_permiso],
            )


class Migration(migrations.Migration):
    dependencies = [("funds", "0001_initial")]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]

"""Valores iniciales para verificación, rescate y permisos del MVP."""

from django.db import migrations


CATALOGOS = {
    "estado_verificacion": ("Pendiente", "Verificada", "Rechazada"),
    "estado_reporte": ("Pendiente", "En atención", "Cerrado"),
    "tipo_reporte": ("Rescate", "Abandono", "Maltrato", "Mascota perdida"),
    "estado_caso": ("En atención", "Cerrado", "Cancelado"),
    "estado_mascota": ("En rescate", "En recuperación", "En adopción", "Adoptada"),
    "sexo_mascota": ("Hembra", "Macho", "Desconocido"),
    "tamano_mascota": ("Pequeño", "Mediano", "Grande"),
    "estado_solicitud_validacion": ("Pendiente", "Aprobada", "Rechazada"),
    "tipo_evidencia": ("Foto", "Documento", "Video"),
}

PERMISOS = {
    "caso.aceptar": "Aceptar un reporte como caso de rescate",
    "caso.cambiar_estado": "Cambiar el estado de un caso asignado",
    "expediente.autorizar": "Otorgar acceso a un expediente bajo custodia",
    "expediente.escribir": "Agregar una anotación médica autorizada",
}

ROLES = {
    "ADMIN_PLATAFORMA": (
        "Administrador de plataforma", "GLOBAL", tuple(PERMISOS)
    ),
    "GESTOR_FUNDACION": (
        "Gestor de fundación", "ENTIDAD",
        ("caso.aceptar", "caso.cambiar_estado", "expediente.autorizar"),
    ),
    "VETERINARIO": (
        "Veterinario verificado", "ENTIDAD", ("expediente.escribir",)
    ),
}


def crear_datos_iniciales(apps, schema_editor):
    TipoMaestro = apps.get_model("core", "TipoMaestro")
    ValorMaestro = apps.get_model("core", "ValorMaestro")
    Rol = apps.get_model("core", "Rol")
    Permiso = apps.get_model("core", "Permiso")
    RolPermiso = apps.get_model("core", "RolPermiso")
    alias = schema_editor.connection.alias

    for nombre_tipo, valores in CATALOGOS.items():
        tipo, _ = TipoMaestro.objects.using(alias).get_or_create(
            nombre=nombre_tipo,
            defaults={"descripcion": nombre_tipo.replace("_", " ")},
        )
        for nombre in valores:
            ValorMaestro.objects.using(alias).get_or_create(tipo=tipo, nombre=nombre)

    permisos = {}
    for codigo, descripcion in PERMISOS.items():
        permiso, _ = Permiso.objects.using(alias).get_or_create(
            codigo=codigo, defaults={"descripcion": descripcion}
        )
        permisos[codigo] = permiso

    for codigo, (nombre, ambito, codigos_permiso) in ROLES.items():
        rol, _ = Rol.objects.using(alias).get_or_create(
            codigo=codigo, defaults={"nombre": nombre, "ambito": ambito}
        )
        for codigo_permiso in codigos_permiso:
            RolPermiso.objects.using(alias).get_or_create(
                rol=rol, permiso=permisos[codigo_permiso]
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]

    operations = [migrations.RunPython(crear_datos_iniciales, migrations.RunPython.noop)]

"""Catálogos y permiso del apadrinamiento."""

from django.db import migrations


def cargar(apps, schema_editor):
    Tipo = apps.get_model("core", "TipoMaestro")
    Valor = apps.get_model("core", "ValorMaestro")
    Permiso = apps.get_model("core", "Permiso")
    Rol = apps.get_model("core", "Rol")
    RolPermiso = apps.get_model("core", "RolPermiso")
    alias = schema_editor.connection.alias
    tipo, _ = Tipo.objects.using(alias).get_or_create(nombre="estado_apadrinamiento")
    for nombre in ("En espera", "Aceptado", "Rechazado", "Cancelado"):
        Valor.objects.using(alias).get_or_create(tipo=tipo, nombre=nombre)
    permiso, _ = Permiso.objects.using(alias).get_or_create(
        codigo="aporte.confirmar",
        defaults={"descripcion": "Confirmar recepción de un aporte por la fundación"},
    )
    for codigo in ("ADMIN_PLATAFORMA", "GESTOR_FUNDACION"):
        rol = Rol.objects.using(alias).get(codigo=codigo)
        RolPermiso.objects.using(alias).get_or_create(rol=rol, permiso=permiso)


class Migration(migrations.Migration):
    dependencies = [("core", "0002_seed_rescue_catalogs")]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]

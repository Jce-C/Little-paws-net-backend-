"""Extensión aditiva: no reemplaza las personalizaciones de roles existentes."""
from django.db import migrations

OPERACIONES = {
    "cuenta.delegar": ("cuenta", "delegar", "ENTIDAD", "RESPONSABLE_PRINCIPAL"),
    "cuenta.aprobar": ("cuenta", "aprobar", "ENTIDAD", "RESPONSABLE_PRINCIPAL"),
    "cuenta.preparar": ("cuenta", "preparar", "AUTORIZADO", None),
    "reclamacion.tomar": ("reclamacion", "tomar", "GLOBAL", "MODERADOR"),
    "reclamacion.resolver": ("reclamacion", "resolver", "ASIGNADO", "MODERADOR"),
    "reclamacion.ejecutar": ("reclamacion", "ejecutar", "ASIGNADO", "MODERADOR"),
}


def cargar(apps, schema_editor):
    alias = schema_editor.connection.alias
    Recurso = apps.get_model("core", "Recurso")
    Permiso = apps.get_model("core", "Permiso")
    Rol = apps.get_model("core", "Rol")
    RP = apps.get_model("core", "RolPermiso")
    for codigo, (recurso, accion, alcance, rol) in OPERACIONES.items():
        r, _ = Recurso.objects.using(alias).get_or_create(codigo=recurso,
            defaults={"nombre": "Cuentas receptoras" if recurso == "cuenta" else "Reclamaciones de titularidad"})
        p, _ = Permiso.objects.using(alias).get_or_create(codigo=codigo, defaults={
            "recurso": r, "accion": accion, "alcance": alcance, "descripcion": f"{r.nombre}: {accion}"})
        if rol:
            RP.objects.using(alias).get_or_create(rol=Rol.objects.using(alias).get(codigo=rol), permiso=p)
    RP.objects.using(alias).get_or_create(
        rol=Rol.objects.using(alias).get(codigo="RESPONSABLE_PRINCIPAL"),
        permiso=Permiso.objects.using(alias).get(codigo="expediente.autorizar"))


class Migration(migrations.Migration):
    dependencies = [("seguridad", "0005_estados_flujos")]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]

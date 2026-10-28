"""Conserva usuarios/asignaciones; no concede los roles nuevos a nadie."""
from django.db import migrations

from ._catalogo_v1 import LEGADOS, POLITICAS, RECURSOS, ROLES


def cargar(apps, schema_editor):
    alias = schema_editor.connection.alias
    Recurso = apps.get_model("core", "Recurso")
    Permiso = apps.get_model("core", "Permiso")
    Rol = apps.get_model("core", "Rol")
    RolPermiso = apps.get_model("core", "RolPermiso")
    recursos = {}
    for codigo, nombre in RECURSOS.items():
        recursos[codigo], _ = Recurso.objects.using(alias).get_or_create(codigo=codigo, defaults={"nombre": nombre})
    permisos = {}
    for codigo, (recurso, accion, alcance) in POLITICAS.items():
        permisos[codigo], _ = Permiso.objects.using(alias).update_or_create(codigo=codigo, defaults={
            "recurso": recursos[recurso], "accion": accion, "alcance": alcance,
            "descripcion": f"{RECURSOS[recurso]}: {accion}", "activo": True,
        })
    for codigo, (nombre, ambito, delegable, codigos) in ROLES.items():
        rol, _ = Rol.objects.using(alias).update_or_create(codigo=codigo, defaults={
            "nombre": nombre, "ambito": ambito, "delegable": delegable, "activo": True, "sistema": True,
        })
        RolPermiso.objects.using(alias).filter(rol=rol).exclude(permiso__codigo__in=codigos).delete()
        for permiso in codigos:
            RolPermiso.objects.using(alias).get_or_create(rol=rol, permiso=permisos[permiso])
    # Se preservan asignaciones históricas, pero se retiran los roles amplios sustituidos.
    Rol.objects.using(alias).filter(codigo__in=LEGADOS).update(activo=False, delegable=False, sistema=True)


class Migration(migrations.Migration):
    dependencies = [("seguridad", "0001_recursos_y_autorizacion")]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]

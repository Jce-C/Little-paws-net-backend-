from django.db import migrations


def cargar(apps, schema_editor):
    db = schema_editor.connection.alias
    recurso = apps.get_model("core", "Recurso")
    permiso = apps.get_model("core", "Permiso")
    rol = apps.get_model("core", "Rol")
    asignacion = apps.get_model("core", "RolPermiso")
    for code, name, roles in (
        ("comunidad.participar", "Publicar, comentar y reaccionar en la comunidad", ["CIUDADANO", "ADMIN_SEGURIDAD"]),
        ("comunidad.moderar", "Retirar publicaciones públicas con motivo", ["MODERADOR", "ADMIN_SEGURIDAD"]),
        ("ayudas.participar", "Registrar y consultar mis intereses de ayuda", ["CIUDADANO", "ADMIN_SEGURIDAD"]),
        ("ayudas.gestionar", "Gestionar convocatorias e intereses de mi organización", ["RESPONSABLE_PRINCIPAL", "RESPONSABLE_SECUNDARIO"]),
    ):
        section, action = code.split(".")
        resource, _ = recurso.objects.using(db).get_or_create(codigo=section, defaults={"nombre": section.title()})
        permission, _ = permiso.objects.using(db).get_or_create(codigo=code, defaults={"recurso": resource, "accion": action, "alcance": "ENTIDAD" if code == "ayudas.gestionar" else "GLOBAL", "descripcion": name, "activo": True})
        for role in rol.objects.using(db).filter(codigo__in=roles):
            asignacion.objects.using(db).get_or_create(rol=role, permiso=permission)
    kind, _ = apps.get_model("core", "TipoMaestro").objects.using(db).get_or_create(nombre="tipo_notificacion")
    apps.get_model("core", "ValorMaestro").objects.using(db).get_or_create(tipo=kind, nombre="Interés de ayuda")


class Migration(migrations.Migration):
    dependencies = [("seguridad", "0019_eliminacion_productos"), ("core", "0011_comunidad_y_ayudas")]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]

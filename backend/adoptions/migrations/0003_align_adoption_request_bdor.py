
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("adoptions", "0002_seed_adoption_catalogs"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="solicitudadopcion",
            name="ck_solicitud_adopcion_fechas",
        ),
        migrations.RemoveIndex(
            model_name="solicitudadopcion",
            name="ix_adop_mascota_estado",
        ),
        migrations.RemoveIndex(
            model_name="solicitudadopcion",
            name="ix_adop_usuario_fecha",
        ),
        migrations.RemoveField(
            model_name="solicitudadopcion",
            name="archivo_soporte",
        ),
        migrations.RemoveField(
            model_name="solicitudadopcion",
            name="fecha_resolucion",
        ),
        migrations.RemoveField(
            model_name="solicitudadopcion",
            name="fundacion",
        ),
        migrations.RemoveField(
            model_name="solicitudadopcion",
            name="observacion_resolucion",
        ),
        migrations.RemoveField(
            model_name="solicitudadopcion",
            name="usuario_resolutor",
        ),
        migrations.RenameField(
            model_name="solicitudadopcion",
            old_name="estado_solicitud",
            new_name="estado_adopcion",
        ),
        migrations.RenameField(
            model_name="solicitudadopcion",
            old_name="observacion_solicitante",
            new_name="observaciones",
        ),
        migrations.RenameField(
            model_name="solicitudadopcion",
            old_name="usuario_solicitante",
            new_name="usuario_adoptante",
        ),
        migrations.AlterField(
            model_name="solicitudadopcion",
            name="estado_adopcion",
            field=models.ForeignKey(
                db_column="id_estado_adopcion",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="solicitudes_adopcion_estado",
                to="core.valormaestro",
            ),
        ),
        migrations.AlterField(
            model_name="solicitudadopcion",
            name="usuario_adoptante",
            field=models.ForeignKey(
                db_column="id_usuario_adoptante",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="solicitudes_adopcion",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="solicitudadopcion",
            index=models.Index(fields=["mascota", "estado_adopcion"], name="ix_adop_mascota_estado"),
        ),
        migrations.AddIndex(
            model_name="solicitudadopcion",
            index=models.Index(fields=["usuario_adoptante", "fecha_solicitud"], name="ix_adop_usuario_fecha"),
        ),
    ]

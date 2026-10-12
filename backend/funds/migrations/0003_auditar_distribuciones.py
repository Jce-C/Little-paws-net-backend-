"""Registrar responsable y fechas sin atribuir datos históricos inventados."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import F, Q


def comprobar_sin_distribuciones(apps, schema_editor):
    Distribucion = apps.get_model("funds", "DistribucionReportadaFondo")
    if Distribucion.objects.using(schema_editor.connection.alias).exists():
        raise RuntimeError(
            "Hay distribuciones existentes sin usuario/fecha de reporte verificables. "
            "No se modificó el esquema; respalde y revise esos registros antes de aplicar esta migración."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("funds", "0002_seed_fund_catalogs"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(comprobar_sin_distribuciones, migrations.RunPython.noop),
        migrations.AddField(
            model_name="distribucionreportadafondo",
            name="usuario_reportador",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT,
                db_column="id_usuario_reportador", related_name="distribuciones_reportadas",
            ),
        ),
        migrations.AddField(
            model_name="distribucionreportadafondo",
            name="fecha_reporte",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name="distribucionreportadafondo",
            name="fecha_confirmacion",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="distribucionreportadafondo",
            name="observacion_confirmacion",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="distribucionreportadafondo",
            name="usuario_confirmador",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT,
                db_column="id_usuario_confirmador", related_name="distribuciones_confirmadas",
                null=True, blank=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="distribucionreportadafondo",
            constraint=models.CheckConstraint(
                condition=Q(fecha_distribucion__lte=F("fecha_reporte")), name="ck_dist_fecha_reporte",
            ),
        ),
        migrations.AddConstraint(
            model_name="distribucionreportadafondo",
            constraint=models.CheckConstraint(
                condition=(
                    Q(usuario_confirmador__isnull=True, fecha_confirmacion__isnull=True, observacion_confirmacion="")
                    | (
                        Q(usuario_confirmador__isnull=False, fecha_confirmacion__isnull=False)
                        & ~Q(observacion_confirmacion="")
                    )
                ),
                name="ck_dist_confirmacion_datos",
            ),
        ),
    ]

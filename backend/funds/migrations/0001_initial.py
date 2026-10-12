import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("core", "0003_seed_sponsorship"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FondoExterno",
            fields=[
                ("id_fondo_externo", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=150, unique=True)),
                ("datos_transferencia_cifrados", models.BinaryField()),
            ],
            options={"db_table": "FondoExterno"},
        ),
        migrations.CreateModel(
            name="DonacionGeneral",
            fields=[
                ("id_donacion", models.AutoField(primary_key=True, serialize=False)),
                ("monto_comprometido", models.DecimalField(max_digits=12, decimal_places=2)),
                ("fecha_compromiso", models.DateTimeField(auto_now_add=True)),
                ("fondo_externo", models.ForeignKey(
                    to="funds.fondoexterno", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_fondo_externo",
                )),
                ("usuario_donante", models.ForeignKey(
                    to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_usuario_donante",
                )),
                ("estado_donacion", models.ForeignKey(
                    to="core.valormaestro", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_estado_donacion", related_name="donaciones_estado",
                )),
            ],
            options={
                "db_table": "DonacionGeneral",
                "constraints": [models.CheckConstraint(
                    condition=models.Q(monto_comprometido__gt=0), name="ck_donacion_monto_pos",
                )],
                "indexes": [
                    models.Index(fields=["fondo_externo", "estado_donacion"], name="ix_donacion_fondo_estado"),
                    models.Index(fields=["usuario_donante", "fecha_compromiso"], name="ix_donacion_donante_fecha"),
                ],
            },
        ),
        migrations.CreateModel(
            name="DistribucionReportadaFondo",
            fields=[
                ("id_distribucion", models.AutoField(primary_key=True, serialize=False)),
                ("monto_reportado", models.DecimalField(max_digits=12, decimal_places=2)),
                ("fecha_distribucion", models.DateTimeField()),
                ("criterio", models.TextField(blank=True)),
                ("fondo_externo", models.ForeignKey(
                    to="funds.fondoexterno", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_fondo_externo",
                )),
                ("estado_distribucion", models.ForeignKey(
                    to="core.valormaestro", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_estado_distribucion",
                )),
                ("fundacion", models.ForeignKey(
                    to="core.fundacion", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_fundacion",
                )),
                ("usuario_confirmador", models.ForeignKey(
                    to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_usuario_confirmador", null=True, blank=True,
                )),
                ("archivo_evidencia", models.ForeignKey(
                    to="core.archivodigital", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_archivo_evidencia", null=True, blank=True,
                )),
            ],
            options={
                "db_table": "DistribucionReportadaFondo",
                "constraints": [models.CheckConstraint(
                    condition=models.Q(monto_reportado__gt=0), name="ck_distribucion_monto_pos",
                )],
                "indexes": [
                    models.Index(fields=["fondo_externo", "estado_distribucion"], name="ix_dist_fondo_estado"),
                    models.Index(fields=["fundacion", "fecha_distribucion"], name="ix_dist_fundacion_fecha"),
                ],
            },
        ),
        migrations.CreateModel(
            name="HistorialEstadoDonacion",
            fields=[
                ("id_historial_donacion", models.AutoField(primary_key=True, serialize=False)),
                ("fecha_cambio", models.DateTimeField(auto_now_add=True)),
                ("observacion", models.TextField(blank=True)),
                ("donacion", models.ForeignKey(
                    to="funds.donaciongeneral", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_donacion",
                )),
                ("estado_anterior", models.ForeignKey(
                    to="core.valormaestro", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_estado_anterior", related_name="donaciones_historial_anterior",
                    null=True, blank=True,
                )),
                ("estado_nuevo", models.ForeignKey(
                    to="core.valormaestro", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_estado_nuevo", related_name="donaciones_historial_nuevo",
                )),
                ("usuario_actor", models.ForeignKey(
                    to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_usuario_actor",
                )),
            ],
            options={
                "db_table": "HistorialEstadoDonacion",
                "indexes": [models.Index(fields=["donacion", "fecha_cambio"], name="ix_hist_donacion_fecha")],
            },
        ),
        migrations.CreateModel(
            name="SolicitudEmergencia",
            fields=[
                ("id_solicitud_emergencia", models.AutoField(primary_key=True, serialize=False)),
                ("motivo", models.TextField()),
                ("monto_solicitado", models.DecimalField(max_digits=12, decimal_places=2)),
                ("fecha_solicitud", models.DateTimeField(auto_now_add=True)),
                ("fundacion", models.ForeignKey(
                    to="core.fundacion", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_fundacion",
                )),
                ("fondo_externo", models.ForeignKey(
                    to="funds.fondoexterno", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_fondo_externo",
                )),
                ("estado_emergencia", models.ForeignKey(
                    to="core.valormaestro", on_delete=django.db.models.deletion.PROTECT,
                    db_column="id_estado_emergencia",
                )),
            ],
            options={
                "db_table": "SolicitudEmergencia",
                "constraints": [
                    models.CheckConstraint(condition=models.Q(monto_solicitado__gt=0), name="ck_emergencia_monto_pos"),
                    models.CheckConstraint(condition=~models.Q(motivo=""), name="ck_emergencia_motivo"),
                ],
                "indexes": [models.Index(fields=["fundacion", "fecha_solicitud"], name="ix_emerg_fundacion_fecha")],
            },
        ),
    ]

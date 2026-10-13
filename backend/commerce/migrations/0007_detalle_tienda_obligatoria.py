import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("commerce", "0006_rellenar_tienda_detalle")]

    operations = [
        migrations.AlterField(
            model_name="detallepedido",
            name="tienda",
            field=models.ForeignKey(
                db_column="id_tienda", on_delete=django.db.models.deletion.PROTECT,
                to="core.tienda",
            ),
        ),
    ]

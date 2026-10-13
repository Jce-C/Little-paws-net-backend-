import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("commerce", "0004_producto_descripcion_en_producto_nombre_en_and_more")]

    operations = [
        migrations.AddField(
            model_name="detallepedido",
            name="tienda",
            field=models.ForeignKey(
                db_column="id_tienda", null=True,
                on_delete=django.db.models.deletion.PROTECT, to="core.tienda",
            ),
        ),
    ]

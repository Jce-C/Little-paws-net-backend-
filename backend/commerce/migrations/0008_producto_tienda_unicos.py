from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("commerce", "0007_detalle_tienda_obligatoria")]

    operations = [
        migrations.AddConstraint(
            model_name="producto",
            constraint=models.UniqueConstraint(
                fields=("id_producto", "tienda"), name="uq_producto_tienda",
            ),
        ),
    ]

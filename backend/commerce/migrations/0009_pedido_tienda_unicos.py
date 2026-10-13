from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("commerce", "0008_producto_tienda_unicos")]

    operations = [
        migrations.AddConstraint(
            model_name="pedidoiniciado",
            constraint=models.UniqueConstraint(
                fields=("id_pedido", "tienda"), name="uq_pedido_tienda",
            ),
        ),
    ]

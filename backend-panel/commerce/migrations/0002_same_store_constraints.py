"""MySQL: un detalle debe pertenecer a la tienda del pedido y del producto."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("commerce", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE `DetallePedido` "
                "ADD CONSTRAINT `fk_detalle_pedido_tienda` "
                "FOREIGN KEY (`id_pedido`, `id_tienda`) "
                "REFERENCES `PedidoIniciado` (`id_pedido`, `id_tienda`) "
                "ON DELETE RESTRICT"
            ),
            reverse_sql="ALTER TABLE `DetallePedido` DROP FOREIGN KEY `fk_detalle_pedido_tienda`",
        ),
        migrations.RunSQL(
            sql=(
                "ALTER TABLE `DetallePedido` "
                "ADD CONSTRAINT `fk_detalle_producto_tienda` "
                "FOREIGN KEY (`id_producto`, `id_tienda`) "
                "REFERENCES `Producto` (`id_producto`, `id_tienda`) "
                "ON DELETE RESTRICT"
            ),
            reverse_sql="ALTER TABLE `DetallePedido` DROP FOREIGN KEY `fk_detalle_producto_tienda`",
        ),
    ]

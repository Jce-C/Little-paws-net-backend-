"""Dos FK compuestas imponen que pedido y producto compartan tienda."""

from django.db import migrations


CLAVES = {
    "fk_detalle_pedido_tienda": (
        "ALTER TABLE DetallePedido ADD CONSTRAINT fk_detalle_pedido_tienda "
        "FOREIGN KEY (id_pedido, id_tienda) REFERENCES PedidoIniciado (id_pedido, id_tienda) "
        "ON UPDATE RESTRICT ON DELETE RESTRICT"
    ),
    "fk_detalle_producto_tienda": (
        "ALTER TABLE DetallePedido ADD CONSTRAINT fk_detalle_producto_tienda "
        "FOREIGN KEY (id_producto, id_tienda) REFERENCES Producto (id_producto, id_tienda) "
        "ON UPDATE RESTRICT ON DELETE RESTRICT"
    ),
}

TRIGGERS_ANTERIORES = (
    "tr_detalle_tienda_insert",
    "tr_detalle_tienda_update",
    "tr_producto_tienda_update",
    "tr_pedido_tienda_update",
)


def aplicar(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return

    # MySQL no revierte DDL. El paso es repetible si se interrumpió a mitad.
    with schema_editor.connection.cursor() as cursor:
        for nombre, sql in CLAVES.items():
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS "
                "WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME = 'DetallePedido' "
                "AND CONSTRAINT_NAME = %s AND CONSTRAINT_TYPE = 'FOREIGN KEY'",
                [nombre],
            )
            if cursor.fetchone()[0] == 0:
                schema_editor.execute(sql)

    for nombre in TRIGGERS_ANTERIORES:
        schema_editor.execute(f"DROP TRIGGER IF EXISTS {nombre}")


class Migration(migrations.Migration):
    dependencies = [("commerce", "0009_pedido_tienda_unicos")]
    operations = [migrations.RunPython(aplicar, atomic=False)]

"""MySQL impide que un pedido mezcle productos de tiendas distintas."""

from django.db import migrations


TRIGGERS = {
    "tr_detalle_tienda_insert": """
        CREATE TRIGGER tr_detalle_tienda_insert BEFORE INSERT ON DetallePedido
        FOR EACH ROW BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM PedidoIniciado p JOIN Producto pr ON p.id_tienda = pr.id_tienda
                WHERE p.id_pedido = NEW.id_pedido AND pr.id_producto = NEW.id_producto
            ) THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El producto no pertenece a la tienda del pedido';
            END IF;
        END
    """,
    "tr_detalle_tienda_update": """
        CREATE TRIGGER tr_detalle_tienda_update BEFORE UPDATE ON DetallePedido
        FOR EACH ROW BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM PedidoIniciado p JOIN Producto pr ON p.id_tienda = pr.id_tienda
                WHERE p.id_pedido = NEW.id_pedido AND pr.id_producto = NEW.id_producto
            ) THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El producto no pertenece a la tienda del pedido';
            END IF;
        END
    """,
    "tr_producto_tienda_update": """
        CREATE TRIGGER tr_producto_tienda_update BEFORE UPDATE ON Producto
        FOR EACH ROW BEGIN
            IF NEW.id_tienda <> OLD.id_tienda AND EXISTS (
                SELECT 1 FROM DetallePedido d WHERE d.id_producto = OLD.id_producto
            ) THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede mover un producto incluido en pedidos';
            END IF;
        END
    """,
    "tr_pedido_tienda_update": """
        CREATE TRIGGER tr_pedido_tienda_update BEFORE UPDATE ON PedidoIniciado
        FOR EACH ROW BEGIN
            IF NEW.id_tienda <> OLD.id_tienda AND EXISTS (
                SELECT 1 FROM DetallePedido d WHERE d.id_pedido = OLD.id_pedido
            ) THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede cambiar la tienda de un pedido con detalles';
            END IF;
        END
    """,
}


def crear(apps, schema_editor):
    if schema_editor.connection.vendor == "mysql":
        creados = []
        try:
            for nombre, sql in TRIGGERS.items():
                schema_editor.execute(sql)
                creados.append(nombre)
        except Exception:
            # MySQL no revierte DDL: retirar solo los disparadores creados aquí.
            for nombre in reversed(creados):
                schema_editor.execute(f"DROP TRIGGER IF EXISTS {nombre}")
            raise


def eliminar(apps, schema_editor):
    if schema_editor.connection.vendor == "mysql":
        for nombre in reversed(tuple(TRIGGERS)):
            schema_editor.execute(f"DROP TRIGGER IF EXISTS {nombre}")


class Migration(migrations.Migration):
    dependencies = [("commerce", "0002_catalogos_permisos")]
    operations = [migrations.RunPython(crear, eliminar)]

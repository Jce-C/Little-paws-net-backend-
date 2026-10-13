from django.db import migrations
from django.db.models import F, OuterRef, Subquery


def rellenar(apps, schema_editor):
    alias = schema_editor.connection.alias
    Detalle = apps.get_model("commerce", "DetallePedido")
    Pedido = apps.get_model("commerce", "PedidoIniciado")
    detalles = Detalle.objects.using(alias)

    if detalles.exclude(pedido__tienda_id=F("producto__tienda_id")).exists():
        raise RuntimeError(
            "Hay detalles con productos de otra tienda; corrija esos datos antes de migrar."
        )

    tienda_pedido = Pedido.objects.using(alias).filter(
        pk=OuterRef("pedido_id")
    ).values("tienda_id")[:1]
    detalles.update(tienda_id=Subquery(tienda_pedido))


class Migration(migrations.Migration):
    dependencies = [("commerce", "0005_detalle_tienda_opcional")]
    operations = [migrations.RunPython(rellenar, migrations.RunPython.noop)]

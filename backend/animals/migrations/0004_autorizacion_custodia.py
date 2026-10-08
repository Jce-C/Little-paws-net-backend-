"""Vincula cada autorización a la custodia que la concedió."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("animals", "0003_seed_especies")]

    operations = [
        migrations.AddField(
            model_name="autorizacionexpediente",
            name="custodia",
            field=models.ForeignKey(
                to="animals.custodiamascota",
                on_delete=django.db.models.deletion.PROTECT,
                db_column="id_custodia",
            ),
        ),
    ]

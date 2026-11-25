from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [migrations.AddField(
        model_name="usuario", name="debe_cambiar_clave",
        field=models.BooleanField(default=False),
    )]

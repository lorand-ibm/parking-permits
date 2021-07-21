import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parking_permits_app", "0011_rename_euro_min_emission_limit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="drivinglicence",
            name="customer",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="driving_licence",
                to="parking_permits_app.customer",
                verbose_name="Customer",
            ),
        ),
    ]

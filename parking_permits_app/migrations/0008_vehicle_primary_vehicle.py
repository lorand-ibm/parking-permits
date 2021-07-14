from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parking_permits_app", "0007_add_euro_emission_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="vehicle",
            name="primary_vehicle",
            field=models.BooleanField(default=True),
        ),
    ]

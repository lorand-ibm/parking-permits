from django.db import migrations, models

import parking_permits_app.constants


class Migration(migrations.Migration):

    dependencies = [
        ("parking_permits_app", "0009_vehicle_euro_class"),
    ]

    operations = [
        migrations.AddField(
            model_name="vehicle",
            name="emission_type",
            field=models.CharField(
                choices=[
                    (parking_permits_app.constants.EmissionType["EURO"], "EURO"),
                    (parking_permits_app.constants.EmissionType["NEDC"], "NEDC"),
                    (parking_permits_app.constants.EmissionType["WLTP"], "WLTP"),
                ],
                max_length=16,
                null=True,
                verbose_name="Emission type",
            ),
        ),
    ]

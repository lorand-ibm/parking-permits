from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parking_permits_app", "0015_alter_parkingpermit_identifier"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vehicle",
            name="primary_vehicle",
        ),
        migrations.AddField(
            model_name="parkingpermit",
            name="primary_vehicle",
            field=models.BooleanField(default=True),
        ),
    ]

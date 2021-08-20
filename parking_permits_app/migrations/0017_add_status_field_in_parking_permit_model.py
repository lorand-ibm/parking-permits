from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "parking_permits_app",
            "0016_move_primary_vehicle_field_from_vehicle_to_parking_permit",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="parkingpermit",
            name="status",
            field=models.CharField(
                choices=[
                    ("DRAFT", "DRAFT"),
                    ("PAID", "PAID"),
                    ("CANCELLED", "CANCELLED"),
                    ("EXPIRED", "EXPIRED"),
                ],
                max_length=32,
                null=True,
                verbose_name="Status",
            ),
        ),
    ]

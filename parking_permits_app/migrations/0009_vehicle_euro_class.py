from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parking_permits_app", "0008_vehicle_primary_vehicle"),
    ]

    operations = [
        migrations.AddField(
            model_name="vehicle",
            name="euro_class",
            field=models.IntegerField(blank=True, null=True, verbose_name="Euro class"),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parking_permits_app", "0010_vehicle_emission_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lowemissioncriteria",
            name="euro_min_emission_limit",
        ),
        migrations.AddField(
            model_name="lowemissioncriteria",
            name="euro_min_class_limit",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Euro minimum class limit"
            ),
        ),
    ]

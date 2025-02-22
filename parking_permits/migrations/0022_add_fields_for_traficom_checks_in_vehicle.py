# Generated by Django 3.2 on 2022-04-07 18:37

import django.utils.timezone
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parking_permits", "0021_update_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="vehicle",
            name="updated_from_traficom_on",
            field=models.DateField(
                default=django.utils.timezone.now,
                verbose_name="Update from traficom on",
            ),
        ),
        migrations.AddField(
            model_name="vehicle",
            name="users",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=15), default=list, size=None
            ),
        ),
    ]

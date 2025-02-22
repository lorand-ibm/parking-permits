# Generated by Django 3.2 on 2022-01-25 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("parking_permits", "0010_add_order_item_date_range"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="permit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order_items",
                to="parking_permits.parkingpermit",
                verbose_name="Parking permit",
            ),
        ),
    ]

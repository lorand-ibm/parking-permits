from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "parking_permits_app",
            "0012_make_customer_one_to_one_in_drivinglicence_model",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="contracttype",
            name="contract_type",
            field=models.CharField(
                choices=[
                    ("Fixed period", "Fixed period"),
                    ("Open ended", "Open ended"),
                ],
                max_length=16,
                verbose_name="Contract type",
            ),
        ),
        migrations.AlterField(
            model_name="vehicle",
            name="category",
            field=models.CharField(
                choices=[
                    ("M1", "M1"),
                    ("M2", "M2"),
                    ("N1", "N1"),
                    ("N2", "N2"),
                    ("L3e", "L3e"),
                    ("L4e", "L4e"),
                    ("L5e", "L5e"),
                    ("L6e", "L6e"),
                ],
                max_length=16,
                verbose_name="Vehicle category",
            ),
        ),
        migrations.AlterField(
            model_name="vehicle",
            name="emission_type",
            field=models.CharField(
                choices=[("EURO", "EURO"), ("NEDC", "NEDC"), ("WLTP", "WLTP")],
                max_length=16,
                null=True,
                verbose_name="Emission type",
            ),
        ),
        migrations.AlterField(
            model_name="vehicletype",
            name="type",
            field=models.CharField(
                choices=[
                    ("Bensin", "Bensin"),
                    ("Diesel", "Diesel"),
                    ("Bifuel", "Bifuel"),
                ],
                max_length=32,
                verbose_name="Type",
            ),
        ),
    ]

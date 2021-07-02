from datetime import date
from importlib import import_module

from django.core.management.base import BaseCommand
from django.db import transaction

from parking_permits_app.models import Product, ProductPrice


class Command(BaseCommand):
    help = "Usage: python manage.py create_products_prices --year 2021 --data-module parking_permits_app.data.2021"

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, required=True)
        parser.add_argument("--data-module", type=str, required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        data_module = import_module(options.get("data_module"))

        for zone_name, zone_price in data_module.ZONE_MONTHLY_PRICES.items():
            obj, created = ProductPrice.objects.get_or_create(
                product=Product.objects.get(name=zone_name),
                price=zone_price,
                start_date=date(day=1, month=1, year=options.get("year")),
                end_date=date(day=31, month=12, year=options.get("year")),
            )

            if created:
                print(f"{obj.product.name} price created")
            else:
                print(f"{obj.product.name} price already exists")

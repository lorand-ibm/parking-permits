from django.core.management.base import BaseCommand
from django.db import transaction

from parking_permits_app.constants import Zone
from parking_permits_app.models import Product


class Command(BaseCommand):
    help = "Usage: python manage.py create_products"

    @transaction.atomic
    def handle(self, *args, **options):
        for zone in Zone:
            product, created = Product.objects.get_or_create(name=zone.value)

            if created:
                print(f"{product.name} created")
            else:
                print(f"{product.name} already exists")

import factory

from parking_permits.models import Price

from .faker import fake
from .zone import ParkingZoneFactory


class PriceFactory(factory.django.DjangoModelFactory):
    zone = factory.SubFactory(ParkingZoneFactory)
    price = fake.random.randint(1, 50)
    year = 2021

    class Meta:
        model = Price

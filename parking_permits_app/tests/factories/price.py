import factory
import pytz

from parking_permits_app.models import Price

from .faker import fake
from .zone import ParkingZoneFactory


class PriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Price

    zone = factory.SubFactory(ParkingZoneFactory)
    price = fake.random.randint(1, 50)
    start_date = factory.LazyFunction(
        lambda: fake.date_time_between(
            start_date="-2h", end_date="-1h", tzinfo=pytz.utc
        )
    )
    end_date = factory.LazyFunction(
        lambda: fake.date_time_between(
            start_date="+1h", end_date="+2h", tzinfo=pytz.utc
        )
    )

import factory
import pytz

from ..models import Product, ProductPrice
from .faker import fake


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: "zone_%d" % (n + 1))


class ProductPriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductPrice

    product = factory.SubFactory(ProductFactory)
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

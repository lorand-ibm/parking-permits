import random
import string

import factory

from parking_permits_app import constants
from parking_permits_app.factories.customer import CustomerFactory
from parking_permits_app.models import Vehicle, VehicleType


def generate_random_registration_number():
    part_1 = "".join(random.choices(string.ascii_uppercase, k=3))
    part_2 = "".join(random.choices(string.digits, k=3))
    return f"{part_1}-{part_2}"


class VehicleTypeFactory(factory.django.DjangoModelFactory):
    type = random.choice(list(constants.VehicleType)).value

    class Meta:
        model = VehicleType


class VehicleFactory(factory.django.DjangoModelFactory):
    type = factory.SubFactory(VehicleTypeFactory)
    category = random.choice(list(constants.VehicleCategory)).value
    manufacturer = factory.Faker("name")
    model = factory.Faker("name")
    production_year = factory.Faker("year")
    registration_number = factory.LazyFunction(generate_random_registration_number)
    emission = random.randint(0, 90)
    last_inspection_date = factory.Faker("date")
    owner = factory.SubFactory(CustomerFactory)
    holder = factory.SubFactory(CustomerFactory)

    class Meta:
        model = Vehicle

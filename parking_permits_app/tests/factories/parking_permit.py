import factory

from parking_permits_app.models import ParkingPermit
from parking_permits_app.tests.factories import ParkingZoneFactory
from parking_permits_app.tests.factories.customer import CustomerFactory
from parking_permits_app.tests.factories.vehicle import VehicleFactory


class ParkingPermitFactory(factory.django.DjangoModelFactory):
    customer = factory.SubFactory(CustomerFactory)
    vehicle = factory.SubFactory(VehicleFactory)
    parking_zone = factory.SubFactory(ParkingZoneFactory)

    class Meta:
        model = ParkingPermit

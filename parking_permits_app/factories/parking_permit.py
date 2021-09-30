import factory

from parking_permits_app.factories import ParkingZoneFactory
from parking_permits_app.factories.customer import CustomerFactory
from parking_permits_app.factories.vehicle import VehicleFactory
from parking_permits_app.models import ParkingPermit


class ParkingPermitFactory(factory.django.DjangoModelFactory):
    customer = factory.SubFactory(CustomerFactory)
    vehicle = factory.SubFactory(VehicleFactory)
    parking_zone = factory.SubFactory(ParkingZoneFactory)

    class Meta:
        model = ParkingPermit

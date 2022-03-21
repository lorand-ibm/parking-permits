import random
from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from parking_permits.models import Vehicle
from parking_permits.models.vehicle import EmissionType, VehicleClass

CARS = [
    {"manufacturer": "Toyota", "model": "CH-R"},
    {"manufacturer": "Toyota", "model": "Corolla"},
    {"manufacturer": "Toyota", "model": "Yaris"},
    {"manufacturer": "Toyota", "model": "Avensis"},
    {"manufacturer": "Toyota", "model": "Aygo"},
    {"manufacturer": "Nissan", "model": "Micra"},
    {"manufacturer": "BMW", "model": "X1"},
    {"manufacturer": "Audi", "model": "A6"},
    {"manufacturer": "VW", "model": "Golf"},
]


def get_mock_vehicle(registration):
    car = random.choice(CARS)
    try:
        vehicle = Vehicle.objects.get(
            Q(registration_number__iexact=registration),
        )
    except ObjectDoesNotExist:
        vehicle = Vehicle.objects.create(
            last_inspection_date=datetime.now() + timedelta(days=365),
            emission_type=EmissionType.WLTP,
            emission=random.randint(50, 150),
            registration_number=registration,
            manufacturer=car.get("manufacturer"),
            model=car.get("model"),
            vehicle_class=VehicleClass.M1,
        )
    return vehicle

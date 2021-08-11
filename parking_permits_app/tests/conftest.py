import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from parking_permits_app.factories import ParkingZoneFactory, PriceFactory

register(PriceFactory)
register(ParkingZoneFactory)


@pytest.fixture
def api_client():
    return APIClient()

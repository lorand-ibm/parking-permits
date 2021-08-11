import pytest
from django.urls import reverse

from ..factories import ParkingZoneFactory
from .utils import get

list_url = reverse("parking_permits_app:v1:product-list")


def get_detail_url(obj):
    return reverse("parking_permits_app:v1:product-detail", kwargs={"pk": obj.pk})


@pytest.mark.django_db
def test_get_zone(api_client):
    zone = ParkingZoneFactory()
    zone_data = get(api_client, get_detail_url(zone))
    assert zone_data["shared_product_id"] is not None
    assert zone_data["name"] == zone.name
    assert zone_data["prices"] is not None

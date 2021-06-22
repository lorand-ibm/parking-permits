import pytest
from django.urls import reverse

from ..factories import ProductFactory
from .utils import get

list_url = reverse("parking_permits_app:v1:product-list")


def get_detail_url(obj):
    return reverse("parking_permits_app:v1:product-detail", kwargs={"pk": obj.pk})


@pytest.mark.django_db
def test_get_product(api_client):
    product = ProductFactory()
    product_data = get(api_client, get_detail_url(product))
    assert product_data["shared_product_id"] is not None
    assert product_data["name"] == product.name
    assert product_data["prices"] is not None

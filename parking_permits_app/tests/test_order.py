from rest_framework.test import APIClient

from .utils import post


def test_post_order():
    api_client = APIClient()
    order_url = "/api/talpa/order/"
    new_order_data = {
        "userId": "UHJvZmlsZU5vZGU6NTI5MjFmZTctOWRjYS00ZmYyLWE4MjgtN",
        "permitId": "ZGU6NTI5MjFmZTctOWRjYS00ZmYyLWE4MjgtN",
        "start_time": "2020-01-01T00:00:00Z",
        "end_time": "2021-12-31T23:59:00Z",
        "status": "VALID",
    }
    response = post(api_client, order_url, new_order_data, 200)
    assert response.get("message") is not None

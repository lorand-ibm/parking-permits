import uuid
from unittest.mock import patch

from django.test import TestCase

from parking_permits.exceptions import CreateTalpaProductError
from parking_permits.tests.factories.product import ProductFactory
from parking_permits.tests.factories.zone import ParkingZoneFactory


class MockResponse:
    reasons = {401: "Forbidden"}

    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self.reason = self.reasons.get(status_code)
        self.json_data = json_data
        self.text = "Error" if status_code != 200 else ""

    def json(self):
        return self.json_data


class TestProduct(TestCase):
    def setUp(self):
        zone = ParkingZoneFactory(name="A")
        self.product = ProductFactory(zone=zone)

    def test_should_return_correct_product_name(self):
        self.assertEqual(self.product.name, "Pysäköintialue A")

    @patch("requests.post", return_value=MockResponse(201, {"productId": uuid.uuid4()}))
    def test_should_save_talpa_product_id_when_creating_talpa_product_successfully(
        self, mock_post
    ):
        self.product.create_talpa_product()
        mock_post.assert_called_once()
        self.assertIsNotNone(self.product.talpa_product_id)

    @patch("requests.post", return_value=MockResponse(401))
    def test_should_raise_error_when_creating_talpa_product_failed(self, mock_post):
        with self.assertRaises(CreateTalpaProductError):
            self.product.create_talpa_product()
            mock_post.assert_called_once()
            self.assertIsNotNone(self.product.talpa_product_id)

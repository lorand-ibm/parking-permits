from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from parking_permits.models.order import OrderStatus
from parking_permits.models.parking_permit import ParkingPermitStatus
from parking_permits.tests.factories.order import OrderFactory
from parking_permits.tests.factories.parking_permit import ParkingPermitFactory


class OrderViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_order_view_should_return_bad_request_if_talpa_order_id_missing(self):
        url = reverse("parking_permits:order-notify")
        data = {
            "eventType": "PAYMENT_PAID",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_order_view_should_update_order_and_permits_status(self):
        talpa_order_id = "D86CA61D-97E9-410A-A1E3-4894873B1B35"
        order = OrderFactory(talpa_order_id=talpa_order_id, status=OrderStatus.DRAFT)
        permit_1 = ParkingPermitFactory(
            order=order, status=ParkingPermitStatus.PAYMENT_IN_PROGRESS
        )
        permit_2 = ParkingPermitFactory(
            order=order, status=ParkingPermitStatus.PAYMENT_IN_PROGRESS
        )
        url = reverse("parking_permits:order-notify")
        data = {"eventType": "PAYMENT_PAID", "orderId": talpa_order_id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        permit_1.refresh_from_db()
        permit_2.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.CONFIRMED)
        self.assertEqual(permit_1.status, ParkingPermitStatus.VALID)
        self.assertEqual(permit_1.status, ParkingPermitStatus.VALID)

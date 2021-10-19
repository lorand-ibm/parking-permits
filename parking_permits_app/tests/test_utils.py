from django.test import TestCase

from parking_permits_app.constants import ParkingPermitStatus
from parking_permits_app.models import ParkingPermit
from parking_permits_app.tests.factories.customer import CustomerFactory
from parking_permits_app.tests.factories.parking_permit import ParkingPermitFactory
from parking_permits_app.utils import apply_filtering, apply_ordering


class ApplyingOrderingTestCase(TestCase):
    def setUp(self):
        customer_1 = CustomerFactory(first_name="Firstname B", last_name="Lastname 1")
        customer_2 = CustomerFactory(first_name="Firstname A", last_name="Lastname 2")
        customer_3 = CustomerFactory(first_name="Firstname A", last_name="Lastname 3")
        ParkingPermitFactory(customer=customer_1)
        ParkingPermitFactory(customer=customer_2)
        ParkingPermitFactory(customer=customer_3)

    def test_apply_asc_ordering(self):
        order_by = {
            "order_fields": ["customer__first_name", "customer__last_name"],
            "order_direction": "ASC",
        }
        qs = ParkingPermit.objects.all()
        ordered_qs = apply_ordering(qs, order_by)
        self.assertEqual(ordered_qs[0].customer.first_name, "Firstname A")
        self.assertEqual(ordered_qs[0].customer.last_name, "Lastname 2")
        self.assertEqual(ordered_qs[1].customer.first_name, "Firstname A")
        self.assertEqual(ordered_qs[1].customer.last_name, "Lastname 3")
        self.assertEqual(ordered_qs[2].customer.first_name, "Firstname B")
        self.assertEqual(ordered_qs[2].customer.last_name, "Lastname 1")

    def test_apply_desc_ordering(self):
        order_by = {
            "order_fields": ["customer__first_name", "customer__last_name"],
            "order_direction": "DESC",
        }
        qs = ParkingPermit.objects.all()
        ordered_qs = apply_ordering(qs, order_by)
        self.assertEqual(ordered_qs[0].customer.first_name, "Firstname B")
        self.assertEqual(ordered_qs[0].customer.last_name, "Lastname 1")
        self.assertEqual(ordered_qs[1].customer.first_name, "Firstname A")
        self.assertEqual(ordered_qs[1].customer.last_name, "Lastname 3")
        self.assertEqual(ordered_qs[2].customer.first_name, "Firstname A")
        self.assertEqual(ordered_qs[2].customer.last_name, "Lastname 2")


class ApplyingFilteringTestCase(TestCase):
    def setUp(self):
        customer_1 = CustomerFactory(first_name="Firstname B", last_name="Lastname 1")
        customer_2 = CustomerFactory(first_name="Firstname A", last_name="Lastname 2")
        customer_3 = CustomerFactory(first_name="Firstname A", last_name="Lastname 3")
        ParkingPermitFactory(
            customer=customer_1, status=ParkingPermitStatus.DRAFT.value
        )
        ParkingPermitFactory(
            customer=customer_2, status=ParkingPermitStatus.VALID.value
        )
        ParkingPermitFactory(
            customer=customer_3, status=ParkingPermitStatus.DRAFT.value
        )

    def test_search_with_model_fields(self):
        all_parking_permits = ParkingPermit.objects.all()
        search_items = [
            {"match_type": "iexact", "fields": ["status"], "value": "VALID"}
        ]
        qs = apply_filtering(all_parking_permits, search_items)
        self.assertEqual(qs.count(), 1)

        search_items = [
            {"match_type": "iexact", "fields": ["status"], "value": "DRAFT"}
        ]
        qs = apply_filtering(all_parking_permits, search_items)
        self.assertEqual(qs.count(), 2)

    def test_search_with_related_model_fields(self):
        all_parking_permits = ParkingPermit.objects.all()
        search_items = [
            {
                "match_type": "istartswith",
                "fields": ["customer__first_name", "customer__last_name"],
                "value": "last",
            }
        ]
        qs = apply_filtering(all_parking_permits, search_items)
        self.assertEqual(qs.count(), 3)

        search_items = [
            {
                "match_type": "iexact",
                "fields": ["customer__first_name", "customer__last_name"],
                "value": "Firstname A",
            }
        ]
        qs = apply_filtering(all_parking_permits, search_items)
        self.assertEqual(qs.count(), 2)

    def test_search_with_multiple_search_items(self):
        all_parking_permits = ParkingPermit.objects.all()
        search_items = [
            {
                "match_type": "iexact",
                "fields": ["customer__first_name", "customer__last_name"],
                "value": "firstname a",
            },
            {"match_type": "iexact", "fields": ["status"], "value": "DRAFT"},
        ]
        qs = apply_filtering(all_parking_permits, search_items)
        self.assertEqual(qs.count(), 1)

from decimal import Decimal

from django.test import TestCase
from freezegun import freeze_time

from parking_permits.exceptions import PriceError
from parking_permits.tests.factories import ParkingZoneFactory, PriceFactory


class ParkingZoneTestCase(TestCase):
    def setUp(self):
        self.zone = ParkingZoneFactory()

    @freeze_time("2021-10-16")
    def test_zone_price_return_correct_price(self):
        PriceFactory(
            zone=self.zone,
            price=Decimal(20),
            year=2021,
        )
        self.assertEqual(self.zone.resident_price, Decimal(20))

    @freeze_time("2021-10-16")
    def test_zone_price_raise_price_error_if_no_price_defined(self):
        with self.assertRaises(PriceError):
            self.zone.resident_price

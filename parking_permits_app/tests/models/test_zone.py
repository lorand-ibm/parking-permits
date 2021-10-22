from datetime import date
from decimal import Decimal

from django.test import TestCase
from freezegun import freeze_time

from parking_permits_app.exceptions import PriceError
from parking_permits_app.tests.factories import ParkingZoneFactory, PriceFactory


class ParkingZoneTestCase(TestCase):
    def setUp(self):
        self.zone = ParkingZoneFactory()

    @freeze_time("2021-10-16")
    def test_zone_price_return_correct_price(self):
        PriceFactory(
            zone=self.zone,
            price=Decimal(20),
            start_date=date(2021, 10, 1),
            end_date=date(2021, 11, 1),
        )
        self.assertEqual(self.zone.price, Decimal(20))

    @freeze_time("2021-10-16")
    def test_zone_price_raise_price_error_if_no_price_defined(self):
        with self.assertRaises(PriceError):
            self.zone.price

    @freeze_time("2021-10-16")
    def test_zone_price_raise_price_error_if_multiple_prices_defined(self):
        PriceFactory(
            zone=self.zone,
            price=Decimal(20),
            start_date=date(2021, 10, 1),
            end_date=date(2021, 11, 1),
        )
        PriceFactory(
            zone=self.zone,
            price=Decimal(30),
            start_date=date(2021, 10, 15),
            end_date=date(2021, 11, 1),
        )
        with self.assertRaises(PriceError):
            self.zone.price

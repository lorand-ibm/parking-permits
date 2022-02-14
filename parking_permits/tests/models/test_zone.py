from datetime import date
from decimal import Decimal

from django.test import TestCase, override_settings
from freezegun import freeze_time

from parking_permits.exceptions import PriceError
from parking_permits.models.product import ProductType
from parking_permits.tests.factories import ParkingZoneFactory, PriceFactory
from parking_permits.tests.factories.product import ProductFactory


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

    @freeze_time("2021-12-20")
    @override_settings(DBUG=True)
    def test_zone_resident_products(self):
        ProductFactory(
            zone=self.zone,
            type=ProductType.RESIDENT,
            start_date=date(2021, 1, 1),
            end_date=date(2021, 6, 30),
        )
        product_1 = ProductFactory(
            zone=self.zone,
            type=ProductType.RESIDENT,
            start_date=date(2021, 7, 1),
            end_date=date(2021, 12, 31),
        )
        product_2 = ProductFactory(
            zone=self.zone,
            type=ProductType.RESIDENT,
            start_date=date(2022, 1, 1),
            end_date=date(2022, 6, 30),
        )
        product_3 = ProductFactory(
            zone=self.zone,
            type=ProductType.RESIDENT,
            start_date=date(2022, 7, 1),
            end_date=date(2022, 12, 31),
        )
        ProductFactory(
            zone=self.zone,
            type=ProductType.COMPANY,
            start_date=date(2022, 1, 1),
            end_date=date(2022, 12, 31),
        )
        self.assertQuerysetEqual(
            self.zone.resident_products,
            [repr(product_1), repr(product_2), repr(product_3)],
            ordered=False,
        )

        @freeze_time("2021-12-20")
        def test_zone_company_products(self):
            ProductFactory(
                zone=self.zone,
                type=ProductType.COMPANY,
                start_date=date(2021, 1, 1),
                end_date=date(2021, 6, 30),
            )
            product_1 = ProductFactory(
                zone=self.zone,
                type=ProductType.COMPANY,
                start_date=date(2021, 7, 1),
                end_date=date(2021, 12, 31),
            )
            product_2 = ProductFactory(
                zone=self.zone,
                type=ProductType.COMPANY,
                start_date=date(2022, 1, 1),
                end_date=date(2022, 6, 30),
            )
            product_3 = ProductFactory(
                zone=self.zone,
                type=ProductType.COMPANY,
                start_date=date(2022, 7, 1),
                end_date=date(2022, 12, 31),
            )
            ProductFactory(
                zone=self.zone,
                type=ProductType.RESIDENT,
                start_date=date(2022, 1, 1),
                end_date=date(2022, 12, 31),
            )
            self.assertQuerysetEqual(
                self.zone.resident_products,
                [repr(product_1), repr(product_2), repr(product_3)],
                ordered=False,
            )

from decimal import Decimal

from django.test import TestCase

from parking_permits.tests.factories.order import OrderFactory, OrderItemFactory


class TestOrder(TestCase):
    def setUp(self):
        self.order = OrderFactory()
        OrderItemFactory(
            order=self.order, unit_price=Decimal(30), quantity=2, vat=Decimal(0.2)
        )
        OrderItemFactory(
            order=self.order, unit_price=Decimal(20), quantity=5, vat=Decimal(0.5)
        )

    def test_should_return_correct_total_price(self):
        self.assertAlmostEqual(self.order.total_price, Decimal(160))

    def test_should_return_correct_total_price_net(self):
        self.assertAlmostEqual(self.order.total_price_net, Decimal(98))

    def test_should_return_correct_total_price_vat(self):
        self.assertAlmostEqual(self.order.total_price_vat, Decimal(62))


class TestOrderItem(TestCase):
    def setUp(self):
        self.order_item = OrderItemFactory(
            unit_price=Decimal(30), quantity=2, vat=Decimal(0.2)
        )

    def test_should_return_correct_unit_price_net(self):
        self.assertAlmostEqual(self.order_item.unit_price_net, Decimal(24))

    def test_should_return_correct_unit_price_vat(self):
        self.assertAlmostEqual(self.order_item.unit_price_vat, Decimal(6))

    def test_should_return_correct_total_price(self):
        self.assertAlmostEqual(self.order_item.total_price, Decimal(60))

    def test_should_return_correct_total_price_net(self):
        self.assertAlmostEqual(self.order_item.total_price_net, Decimal(48))

    def test_should_return_correct_total_price_vat(self):
        self.assertAlmostEqual(self.order_item.total_price_vat, Decimal(12))

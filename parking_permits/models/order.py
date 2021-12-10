from django.db import models
from django.utils.translation import gettext_lazy as _

from parking_permits.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin

from .customer import Customer
from .parking_permit import ParkingPermit
from .product import Product


class OrderType(models.TextChoices):
    ORDER = "ORDER", _("Order")
    SUBSCRIPTION = "SUBSCRIPTION", _("Subscription")


class OrderStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    CONFIRMED = "CONFIRMED", _("Confirmed")
    CANCELLED = "CANCELLED", _("Cancelled")


class Order(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    talpa_order_id = models.UUIDField(
        _("Talpa order id"), unique=True, editable=False, null=True, blank=True
    )
    talpa_subscription_id = models.UUIDField(
        _("Talpa subscription id"), unique=True, editable=False, null=True, blank=True
    )
    customer = models.ForeignKey(
        Customer,
        verbose_name=_("Customer"),
        related_name="orders",
        on_delete=models.PROTECT,
    )
    order_type = models.CharField(
        _("Order type"),
        max_length=50,
        choices=OrderType.choices,
        default=OrderType.ORDER,
    )
    status = models.CharField(
        _("Order status"),
        max_length=50,
        choices=OrderStatus.choices,
        default=OrderStatus.DRAFT,
    )

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order: {self.id} ({self.order_type})"

    @property
    def total_price(self):
        return sum([item.total_price for item in self.order_items.all()])

    @property
    def total_price_net(self):
        return sum([item.total_price_net for item in self.order_items.all()])

    @property
    def total_price_vat(self):
        return sum([item.total_price_vat for item in self.order_items.all()])


class OrderItem(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    talpa_order_item_id = models.UUIDField(
        _("Talpa order item id"), unique=True, editable=False, null=True, blank=True
    )
    order = models.ForeignKey(
        Order,
        verbose_name=_("Order"),
        related_name="order_items",
        on_delete=models.PROTECT,
    )
    product = models.ForeignKey(
        Product, verbose_name=_("Product"), on_delete=models.PROTECT
    )
    permit = models.OneToOneField(
        ParkingPermit,
        verbose_name=_("Parking permit"),
        related_name="order_item",
        on_delete=models.PROTECT,
    )
    unit_price = models.DecimalField(_("Unit price"), max_digits=6, decimal_places=2)
    vat = models.DecimalField(_("VAT"), max_digits=4, decimal_places=2)
    quantity = models.IntegerField(_("Quantity"))

    class Meta:
        verbose_name = _("Order item")
        verbose_name_plural = _("Order items")

    def __str__(self):
        return f"Order item: {self.id}"

    @property
    def unit_price_net(self):
        return self.unit_price * (1 - self.vat)

    @property
    def unit_price_vat(self):
        return self.unit_price * self.vat

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    @property
    def total_price_net(self):
        return self.total_price * (1 - self.vat)

    @property
    def total_price_vat(self):
        return self.total_price * self.vat

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .customer import Customer
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class RefundStatus(models.TextChoices):
    OPEN = "OPEN", _("Open")
    IN_PROGRESS = "IN_PROGRESS", _("In progress")
    ACCEPTED = "ACCEPTED", _("Accepted")


class Refund(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    customer = models.ForeignKey(
        Customer,
        verbose_name=_("Customer"),
        on_delete=models.PROTECT,
    )
    permit = models.OneToOneField(
        "ParkingPermit",
        verbose_name=_("Permit"),
        on_delete=models.PROTECT,
        related_name="refund",
    )
    amount = models.DecimalField(
        _("Amount"), default=0.00, max_digits=6, decimal_places=2
    )
    iban = models.CharField(max_length=30)
    status = models.CharField(
        _("Status"),
        max_length=32,
        choices=RefundStatus.choices,
        default=RefundStatus.OPEN,
    )

    class Meta:
        verbose_name = _("Refund")
        verbose_name_plural = _("Refunds")

    def __str__(self):
        return "%s -> %s -> %s" % (
            self.customer,
            self.permit,
            str(self.amount),
        )

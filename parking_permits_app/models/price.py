from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .parking_zone import ParkingZone


class Price(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    zone = models.ForeignKey(
        ParkingZone,
        verbose_name=_("Zone"),
        on_delete=models.PROTECT,
        related_name="prices",
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        _("Price"), blank=False, null=False, max_digits=6, decimal_places=2
    )
    start_date = models.DateField(_("Start date"), blank=False, null=False)
    end_date = models.DateField(_("End date"), blank=True, null=True)

    class Meta:
        db_table = "price"
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")

    def __str__(self):
        return "%s %s - %s -> %s" % (
            self.id,
            self.start_date,
            self.end_date,
            str(self.price),
        )

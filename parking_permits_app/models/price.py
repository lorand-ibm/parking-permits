from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class Price(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    COMPANY = "company"
    RESIDENT = "resident"
    TYPE_CHOICES = [(RESIDENT, _("Resident")), (COMPANY, _("Company"))]
    zone = models.ForeignKey(
        "ParkingZone",
        verbose_name=_("Zone"),
        on_delete=models.PROTECT,
        related_name="prices",
    )
    price = models.DecimalField(_("Price"), max_digits=6, decimal_places=2)
    type = models.CharField(
        _("Type"), max_length=20, choices=TYPE_CHOICES, default=RESIDENT
    )
    year = models.IntegerField(_("Year"))

    class Meta:
        db_table = "price"
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")
        unique_together = ["zone", "type", "year"]

    def __str__(self):
        return f"{self.price}€ ({self.year})"

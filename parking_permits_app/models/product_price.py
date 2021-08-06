from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from . import Product
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class ProductPrice(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product price"),
        on_delete=models.PROTECT,
        related_name="prices",
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        _("Product price"), blank=False, null=False, max_digits=6, decimal_places=2
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

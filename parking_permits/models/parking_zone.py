import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..exceptions import PriceError
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .price import Price, PriceType

logger = logging.getLogger(__name__)


class ParkingZoneManager(models.Manager):
    def get_for_location(self, location):
        return self.get(location__intersects=location)


class ParkingZone(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(_("Name"), max_length=128, unique=True)
    description = models.TextField(_("Description"), blank=True)
    description_sv = models.TextField(_("Description sv"), blank=True)
    shared_product_id = models.UUIDField(
        unique=True, editable=False, blank=True, null=True
    )
    location = models.MultiPolygonField(_("Area (2D)"), srid=settings.SRID)

    objects = ParkingZoneManager()

    class Meta:
        verbose_name = _("Parking zone")
        verbose_name_plural = _("Parking zones")

    def __str__(self):
        return self.name

    @property
    def namespace(self):
        return settings.NAMESPACE

    @property
    def price(self):
        logger.warning(
            "price properly is deprecated and will be removed, use resident_price or company_price"
        )
        return self.resident_price

    @property
    def resident_price(self):
        try:
            price = self.prices.get(type=PriceType.RESIDENT, year=timezone.now().year)
        except Price.DoesNotExist:
            raise PriceError("No resident price available")
        return price.price

    @property
    def company_price(self):
        try:
            price = self.prices.get(type=PriceType.COMPANY, year=timezone.now().year)
        except Price.DoesNotExist:
            raise PriceError("No company price available")
        return price.price

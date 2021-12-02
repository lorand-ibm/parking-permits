import json
import logging

import requests
from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..exceptions import PriceError
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .price import Price

logger = logging.getLogger(__name__)


class ParkingZoneManager(models.Manager):
    def get_for_location(self, location):
        return self.get(location__intersects=location)


class ParkingZone(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(_("Name"), max_length=128)
    description = models.TextField(_("Description"), blank=True)
    description_sv = models.TextField(_("Description sv"), blank=True)
    shared_product_id = models.UUIDField(
        unique=True, editable=False, blank=True, null=True
    )
    location = models.MultiPolygonField(_("Area (2D)"), srid=settings.SRID)

    objects = ParkingZoneManager()

    class Meta:
        db_table = "parking_zone"
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
            price = self.prices.get(type=Price.RESIDENT, year=timezone.now().year)
        except Price.DoesNotExist:
            raise PriceError("No resident price available")
        return price.price

    @property
    def company_price(self):
        try:
            price = self.prices.get(type=Price.COMPANY, year=timezone.now().year)
        except Price.DoesNotExist:
            raise PriceError("No company price available")
        return price.price


def post_zone_to_talpa(sender, instance, created, **kwargs):
    if not instance.shared_product_id:
        data = {
            "namespace": settings.NAMESPACE,
            "namespaceEntityId": instance.pk,
            "name": instance.name,
        }
        headers = {
            "api-key": settings.TALPA_API_KEY,
        }
        result = requests.post(
            settings.TALPA_PRODUCT_EXPERIENCE_API, data=data, headers=headers
        )
        if result.status_code == 201:
            response = json.loads(result.text)
            instance.shared_product_id = response["productId"]
            instance.save()
        if result.status_code >= 300:
            raise Exception("Failed to create product on talpa: {}".format(result.text))


if not settings.DEBUG:
    # we don't want to run this in DEV and TESTING
    post_save.connect(post_zone_to_talpa, sender=ParkingZone)

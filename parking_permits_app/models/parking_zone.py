import json
from datetime import datetime

import requests
from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class ParkingZone(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(_("Name"), max_length=128, blank=False, null=False)
    description = models.TextField(_("Description"), blank=True, null=True)
    shared_product_id = models.UUIDField(
        unique=True, editable=False, blank=True, null=True
    )
    location = models.MultiPolygonField(
        _("Area (2D)"), srid=settings.SRID, blank=False, null=False
    )

    def get_current_price(self):
        product_price = self.prices.get(
            start_date__lte=datetime.today(),
            end_date__gte=datetime.today(),
        )
        return product_price.price if product_price else None

    class Meta:
        db_table = "parking_zone"
        verbose_name = _("Parking zone")
        verbose_name_plural = _("Parking zones")

    def __str__(self):
        return "%s (%s)" % (self.name, self.id)

    @property
    def namespace(self):
        return settings.NAMESPACE


def post_zone_to_talpa(sender, instance, created, **kwargs):
    if not instance.shared_product_id:
        data = {
            "namespace": settings.NAMESPACE,
            "namespaceEntityId": instance.pk,
            "name": instance.name,
        }
        result = requests.post(settings.TALPA_PRODUCT_EXPERIENCE_API, data=data)
        if result.status_code == 201:
            response = json.loads(result.text)
            instance.shared_product_id = response["productId"]
            instance.save()
        if result.status_code >= 300:
            raise Exception("Failed to create product on talpa: {}".format(result.text))


post_save.connect(post_zone_to_talpa, sender=ParkingZone)

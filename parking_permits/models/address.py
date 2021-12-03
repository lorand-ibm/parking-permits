from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .common import SourceSystem
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .parking_zone import ParkingZone


class Address(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    source_system = models.CharField(
        _("Source system"), max_length=50, choices=SourceSystem.choices, blank=True
    )
    source_id = models.CharField(_("Source id"), max_length=100, blank=True)
    street_name = models.CharField(_("Street name"), max_length=128)
    street_name_sv = models.CharField(_("Street name sv"), max_length=128, blank=True)
    street_number = models.CharField(_("Street number"), max_length=128)
    city = models.CharField(_("City"), max_length=128)
    city_sv = models.CharField(_("City sv"), max_length=128, blank=True)
    postal_code = models.CharField(_("Postal code"), max_length=5, blank=True)
    location = models.PointField(
        _("Location (2D)"), srid=settings.SRID, blank=True, null=True
    )
    primary = models.BooleanField(_("Primary address"), default=False)
    zone = models.ForeignKey(
        ParkingZone,
        verbose_name=_("Zone"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return "%s %s, %s" % (
            self.street_name,
            self.street_number,
            self.city,
        )

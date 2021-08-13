from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .parking_zone import ParkingZone


class Address(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    street_name = models.CharField(
        _("Street name"), max_length=128, blank=False, null=False
    )
    street_number = models.CharField(
        _("Street number"), max_length=128, blank=False, null=False
    )
    city = models.CharField(_("City"), max_length=128, blank=False, null=False)
    location = models.PointField(
        _("Location (2D)"), srid=settings.SRID, blank=False, null=False
    )
    zone = models.ForeignKey(
        ParkingZone,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Zone"),
    )

    class Meta:
        db_table = "address"
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return "%s %s, %s" % (
            self.street_name,
            self.street_number,
            self.city,
        )

    def get_zone(self):
        if not self.location:
            return None
        return ParkingZone.objects.filter(location__intersects=self.location).first()

    def save(self, update_fields=None, *args, **kwargs):
        if update_fields is None or "zone" in update_fields:
            self.zone = self.get_zone()

        super().save(update_fields=update_fields, *args, **kwargs)

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


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
    zone = models.ForeignKey("Zone", verbose_name=_("Zone"), on_delete=models.PROTECT)

    class Meta:
        db_table = "address"
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return "%s - %s %s, %s" % (
            self.id,
            self.street_name,
            self.street_number,
            self.city,
        )

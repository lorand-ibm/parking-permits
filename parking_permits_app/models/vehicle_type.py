from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from parking_permits_app import constants

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class VehicleType(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    type = models.CharField(
        _("Type"),
        max_length=32,
        blank=False,
        null=False,
        choices=[(tag.value, tag.value) for tag in constants.VehicleType],
    )

    class Meta:
        db_table = "vehicle_type"
        verbose_name = _("Vehicle type")
        verbose_name_plural = _("Vehicle types")

    def __str__(self):
        return "%s" % self.type

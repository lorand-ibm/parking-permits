from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


# TODO: Some of these fields should come directly from Helsinki profile User-model.
#  Check how to combine this model with Helsinki profile User-model.
class Customer(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    first_name = models.CharField(_("First name"), max_length=32)
    last_name = models.CharField(_("Last name"), max_length=32)
    national_id_number = models.CharField(
        _("National identification number"), max_length=16
    )
    primary_address = models.ForeignKey(
        "Address",
        verbose_name=_("Primary address"),
        on_delete=models.PROTECT,
        related_name="customers_primary_address",
    )
    other_address = models.ForeignKey(
        "Address",
        verbose_name=_("Other address"),
        on_delete=models.PROTECT,
        related_name="customers_other_address",
        blank=True,
        null=True,
    )
    email = models.CharField(_("Email"), max_length=128, blank=True, null=True)
    phone_number = models.CharField(
        _("Phone number"), max_length=32, blank=True, null=True
    )
    parking_zone = models.ForeignKey(
        "ParkingZone", verbose_name=_("Parking zone"), on_delete=models.PROTECT
    )

    def has_valid_address_within_zone(self):
        if self.primary_address.location.within(self.parking_zone.location):
            return True

        elif self.other_address and self.other_address.location.within(
            self.parking_zone.location
        ):
            return True

        else:
            return False

    def is_owner_or_holder_of_vehicle(self, vehicle):
        return vehicle.owner == self or vehicle.holder == self

    class Meta:
        db_table = "customer"
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self):
        return "%s - %s %s" % (self.id, self.first_name, self.last_name)

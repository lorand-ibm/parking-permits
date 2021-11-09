from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin


class Customer(TimestampedModelMixin):
    id = models.TextField(primary_key=True, unique=True, editable=False)
    user = models.OneToOneField(
        get_user_model(),
        related_name="customer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    first_name = models.CharField(_("First name"), max_length=32)
    last_name = models.CharField(_("Last name"), max_length=32)
    national_id_number = models.CharField(
        _("National identification number"), max_length=16, blank=True, null=True
    )
    primary_address = models.ForeignKey(
        "Address",
        verbose_name=_("Primary address"),
        on_delete=models.PROTECT,
        related_name="customers_primary_address",
        null=True,
        blank=True,
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
    address_security_ban = models.BooleanField(_("Address security ban"), default=False)
    driver_license_checked = models.BooleanField(
        _("Driver's license checked"), default=False
    )

    def is_owner_or_holder_of_vehicle(self, vehicle):
        return vehicle.owner == self or vehicle.holder == self

    class Meta:
        db_table = "customer"
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from helsinki_gdpr.models import SerializableMixin

from .common import SourceSystem
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class Customer(SerializableMixin, TimestampedModelMixin, UUIDPrimaryKeyMixin):
    source_system = models.CharField(
        _("Source system"), max_length=50, choices=SourceSystem.choices, blank=True
    )
    source_id = models.CharField(_("Source id"), max_length=100, blank=True)
    user = models.OneToOneField(
        get_user_model(),
        related_name="customer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    first_name = models.CharField(_("First name"), max_length=32, blank=True)
    last_name = models.CharField(_("Last name"), max_length=32, blank=True)
    national_id_number = models.CharField(
        _("National identification number"), max_length=16, unique=True, blank=True
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
    email = models.CharField(_("Email"), max_length=128, blank=True)
    phone_number = models.CharField(_("Phone number"), max_length=32, blank=True)
    address_security_ban = models.BooleanField(_("Address security ban"), default=False)
    driver_license_checked = models.BooleanField(
        _("Driver's license checked"), default=False
    )
    zone = models.ForeignKey(
        "ParkingZone",
        verbose_name=_("Zone"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    serialize_fields = (
        {"name": "first_name"},
        {"name": "last_name"},
        {"name": "national_id_number"},
        {"name": "email"},
        {"name": "phone_number"},
        {"name": "primary_address", "accessor": lambda a: a.serialize()},
        {"name": "other_address", "accessor": lambda a: a.serialize()},
        {"name": "orders"},
        {"name": "permits"},
    )

    @property
    def age(self):
        ssn = self.national_id_number
        key_centuries = {"+": "18", "-": "19", "A": "20"}
        date_of_birth = datetime(
            year=int(key_centuries[ssn[6]] + ssn[4:6]),
            month=int(ssn[2:4]),
            day=int(ssn[0:2]),
        )
        return relativedelta(datetime.today(), date_of_birth).years

    def is_owner_or_holder_of_vehicle(self, vehicle):
        return vehicle.owner == self or vehicle.holder == self

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

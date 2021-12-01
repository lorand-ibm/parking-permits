from datetime import datetime

import arrow
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from parking_permits_app import constants

from .customer import Customer
from .low_emission_criteria import LowEmissionCriteria
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .vehicle_type import VehicleType


class Vehicle(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    type = models.ForeignKey(
        VehicleType,
        verbose_name=_("Vehicle type"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    category = models.CharField(
        _("Vehicle category"),
        max_length=16,
        choices=[(tag.value, tag.value) for tag in constants.VehicleCategory],
    )
    manufacturer = models.CharField(_("Vehicle manufacturer"), max_length=32)
    model = models.CharField(_("Vehicle model"), max_length=32)
    production_year = models.IntegerField(
        _("Vehicle production_year"), blank=True, null=True
    )
    registration_number = models.CharField(
        _("Vehicle registration number"), max_length=24
    )
    euro_class = models.IntegerField(_("Euro class"), blank=True, null=True)
    emission = models.IntegerField(_("Emission"), blank=True, null=True)
    low_emission_vehicle = models.BooleanField(_("Low emission vehicle"), default=False)
    consent_low_emission_accepted = models.BooleanField(default=False)
    emission_type = models.CharField(
        _("Emission type"),
        max_length=16,
        default=constants.EmissionType.EURO.value,
        choices=[(tag.value, tag.value) for tag in constants.EmissionType],
    )
    serial_number = models.CharField(_("Serial number"), max_length=50, blank=True)
    last_inspection_date = models.DateField(
        _("Last inspection date"), null=True, blank=True
    )
    owner = models.ForeignKey(
        Customer,
        verbose_name=_("Owner"),
        on_delete=models.PROTECT,
        related_name="vehicles_owner",
        null=True,
        blank=True,
    )
    holder = models.ForeignKey(
        Customer,
        verbose_name=_("Holder"),
        on_delete=models.PROTECT,
        related_name="vehicles_holder",
        null=True,
        blank=True,
    )

    def is_due_for_inspection(self):
        return arrow.utcnow().date() > self.last_inspection_date

    @property
    def is_low_emission(self):
        if self.low_emission_vehicle:
            return True

        le_criteria = LowEmissionCriteria.objects.get(
            vehicle_type=self.type,
            start_date__lte=datetime.today(),
            end_date__gte=datetime.today(),
        )

        if not self.euro_class or self.euro_class < le_criteria.euro_min_class_limit:
            return False

        if self.emission_type == constants.EmissionType.NEDC.value:
            return self.emission <= le_criteria.nedc_max_emission_limit
        if self.emission_type == constants.EmissionType.WLTP.value:
            return self.emission <= le_criteria.wltp_max_emission_limit

        return False

    class Meta:
        db_table = "vehicle"
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")

    def __str__(self):
        return "%s (%s, %s)" % (
            self.registration_number,
            self.manufacturer,
            self.model,
        )

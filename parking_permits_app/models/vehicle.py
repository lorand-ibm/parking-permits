from datetime import datetime

import arrow
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from parking_permits_app import constants

from ..pricing.low_emission import is_low_emission
from .customer import Customer
from .low_emission_criteria import LowEmissionCriteria
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .vehicle_type import VehicleType


class Vehicle(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    type = models.ForeignKey(
        VehicleType,
        verbose_name=_("Vehicle type"),
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    category = models.CharField(
        _("Vehicle category"),
        max_length=16,
        blank=False,
        null=False,
        choices=[(tag.value, tag.value) for tag in constants.VehicleCategory],
    )
    manufacturer = models.CharField(
        _("Vehicle manufacturer"), max_length=32, blank=False, null=False
    )
    model = models.CharField(_("Vehicle model"), max_length=32, blank=False, null=False)
    production_year = models.IntegerField(
        _("Vehicle production_year"), blank=False, null=False
    )
    registration_number = models.CharField(
        _("Vehicle registration number"), max_length=24, blank=False, null=False
    )
    euro_class = models.IntegerField(_("Euro class"), blank=True, null=True)
    emission = models.IntegerField(_("Emission"), blank=False, null=False)
    emission_type = models.CharField(
        _("Emission type"),
        max_length=16,
        blank=False,
        null=True,
        choices=[(tag.value, tag.value) for tag in constants.EmissionType],
    )
    last_inspection_date = models.DateField(
        _("Last inspection date"), blank=False, null=False
    )
    owner = models.ForeignKey(
        Customer,
        verbose_name=_("Owner"),
        on_delete=models.PROTECT,
        related_name="vehicles_owner",
    )
    holder = models.ForeignKey(
        Customer,
        verbose_name=_("Holder"),
        on_delete=models.PROTECT,
        related_name="vehicles_holder",
    )
    primary_vehicle = models.BooleanField(null=False, default=True)

    def is_due_for_inspection(self):
        return arrow.utcnow().date() > self.last_inspection_date

    def is_low_emission(self):
        nedc_emission = (
            self.emission
            if self.emission_type == constants.EmissionType.NEDC.value
            else 0
        )
        wltp_emission = (
            self.emission
            if self.emission_type == constants.EmissionType.WLTP.value
            else 0
        )

        low_emission_criteria = LowEmissionCriteria.objects.get(
            vehicle_type=self.type,
            start_date__lte=datetime.today(),
            end_date__gte=datetime.today(),
        )

        return is_low_emission(
            euro_class=self.euro_class,
            euro_class_min_limit=low_emission_criteria.euro_min_class_limit,
            nedc_emission=nedc_emission,
            nedc_emission_max_limit=low_emission_criteria.nedc_max_emission_limit,
            wltp_emission=wltp_emission,
            wltp_emission_max_limit=low_emission_criteria.wltp_max_emission_limit,
        )

    class Meta:
        db_table = "vehicle"
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")

    def __str__(self):
        return "%s - %s, %s, %s, %s" % (
            self.id,
            self.type,
            self.category,
            self.manufacturer,
            self.model,
        )

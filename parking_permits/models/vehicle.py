from datetime import datetime

import arrow
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class VehiclePowerType(models.TextChoices):
    BENSIN = "BENSIN", _("Bensin")
    DIESEL = "DIESEL", _("Diesel")
    BIFUEL = "BIFUEL", _("Bibuel")


class VehicleCategory(models.TextChoices):
    M1 = "M1"
    M2 = "M2"
    N1 = "N1"
    N2 = "N2"
    L3e = "L3e"
    L4e = "L4e"
    L5e = "L5e"
    L6e = "L6e"


class EmissionType(models.TextChoices):
    EURO = "EURO"
    NEDC = "NEDC"
    WLTP = "WLTP"


class LowEmissionCriteria(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    power_type = models.CharField(
        _("Power type"), max_length=50, choices=VehiclePowerType.choices
    )
    nedc_max_emission_limit = models.IntegerField(
        _("NEDC maximum emission limit"), blank=True, null=True
    )
    wltp_max_emission_limit = models.IntegerField(
        _("WLTP maximum emission limit"), blank=True, null=True
    )
    euro_min_class_limit = models.IntegerField(
        _("Euro minimum class limit"), blank=True, null=True
    )
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"), blank=True, null=True)

    class Meta:
        verbose_name = _("Low-emission criteria")
        verbose_name_plural = _("Low-emission criterias")

    def __str__(self):
        return "%s, NEDC: %s, WLTP: %s, EURO: %s" % (
            self.power_type,
            self.nedc_max_emission_limit,
            self.wltp_max_emission_limit,
            self.euro_min_class_limit,
        )


class Vehicle(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    power_type = models.CharField(
        _("Power type"), max_length=50, choices=VehiclePowerType.choices, blank=True
    )
    category = models.CharField(
        _("Category"), max_length=16, choices=VehicleCategory.choices, blank=True
    )
    manufacturer = models.CharField(_("Manufacturer"), max_length=100)
    model = models.CharField(_("Model"), max_length=100)
    production_year = models.IntegerField(_("Production year"), blank=True, null=True)
    registration_number = models.CharField(
        _("Registration number"), max_length=24, unique=True
    )
    euro_class = models.IntegerField(_("Euro class"), blank=True, null=True)
    emission = models.IntegerField(_("Emission"), blank=True, null=True)
    low_emission_vehicle = models.BooleanField(_("Low emission vehicle"), default=False)
    consent_low_emission_accepted = models.BooleanField(default=False)
    emission_type = models.CharField(
        _("Emission type"),
        max_length=16,
        choices=EmissionType.choices,
        default=EmissionType.EURO,
    )
    serial_number = models.CharField(_("Serial number"), max_length=100, blank=True)
    last_inspection_date = models.DateField(
        _("Last inspection date"), null=True, blank=True
    )
    owner = models.ForeignKey(
        "Customer",
        verbose_name=_("Owner"),
        on_delete=models.PROTECT,
        related_name="vehicles_owner",
        null=True,
        blank=True,
    )
    holder = models.ForeignKey(
        "Customer",
        verbose_name=_("Holder"),
        on_delete=models.PROTECT,
        related_name="vehicles_holder",
        null=True,
        blank=True,
    )

    def is_due_for_inspection(self):
        return (
            self.last_inspection_date is not None
            and arrow.utcnow().date() > self.last_inspection_date
        )

    @property
    def is_low_emission(self):
        if self.low_emission_vehicle:
            return True

        try:
            le_criteria = LowEmissionCriteria.objects.get(
                power_type=self.power_type,
                start_date__lte=datetime.today(),
                end_date__gte=datetime.today(),
            )
        except LowEmissionCriteria.DoesNotExist:
            return False

        if not self.euro_class or self.euro_class < le_criteria.euro_min_class_limit:
            return False

        if self.emission_type == EmissionType.NEDC:
            return self.emission <= le_criteria.nedc_max_emission_limit
        if self.emission_type == EmissionType.WLTP:
            return self.emission <= le_criteria.wltp_max_emission_limit

        return False

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")

    def __str__(self):
        return "%s (%s, %s)" % (
            self.registration_number,
            self.manufacturer,
            self.model,
        )

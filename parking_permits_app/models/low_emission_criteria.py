from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .vehicle_type import VehicleType


class LowEmissionCriteria(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    vehicle_type = models.ForeignKey(
        VehicleType,
        verbose_name=_("Vehicle type"),
        on_delete=models.PROTECT,
        blank=False,
        null=False,
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
    start_date = models.DateField(_("Start date"), blank=False, null=False)
    end_date = models.DateField(_("End date"), blank=True, null=True)

    class Meta:
        db_table = "low_emission_criteria"
        verbose_name = _("Low-emission criteria")
        verbose_name_plural = _("Low-emission criterias")

    def __str__(self):
        return "%s - %s, NEDC: %s, WLTP: %s, EURO: %s" % (
            self.id,
            self.vehicle_type,
            self.nedc_max_emission_limit,
            self.wltp_max_emission_limit,
            self.euro_min_class_limit,
        )

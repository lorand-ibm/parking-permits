from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from parking_permits_app import constants

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class ContractType(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    contract_type = models.CharField(
        _("Contract type"),
        max_length=16,
        blank=False,
        null=False,
        choices=[(tag.value, tag.value) for tag in constants.ContractType],
    )
    month_count = models.IntegerField(_("Month count"), blank=True, null=True)

    class Meta:
        db_table = "contract_type"
        verbose_name = _("Contract type")
        verbose_name_plural = _("Contract types")

    def __str__(self):
        return "%s - %s, months: %s" % (self.id, self.contract_type, self.month_count)

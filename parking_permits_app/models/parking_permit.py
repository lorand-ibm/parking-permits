import decimal

import reversion
from django.contrib.gis.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .. import constants
from ..constants import (
    LOW_EMISSION_DISCOUNT,
    SECONDARY_VEHICLE_PRICE_INCREASE,
    ContractType,
    ParkingPermitEndType,
    ParkingPermitStatus,
)
from ..exceptions import PermitCanNotBeEnded, RefundCanNotBeCreated
from ..utils import diff_months_ceil, get_end_time
from .customer import Customer
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .parking_zone import ParkingZone
from .refund import Refund
from .vehicle import Vehicle


def get_next_identifier():
    last = ParkingPermit.objects.order_by("-identifier").first()
    if not last:
        return 80000000
    return last.identifier + 1


class ParkingPermitManager(models.Manager):
    def active(self):
        active_status = [
            ParkingPermitStatus.VALID.value,
            ParkingPermitStatus.PAYMENT_IN_PROGRESS.value,
        ]
        return self.filter(status__in=active_status)

    def active_after(self, time):
        return self.active().filter(Q(end_time__isnull=True) | Q(end_time__gt=time))


@reversion.register()
class ParkingPermit(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    customer = models.ForeignKey(
        Customer,
        verbose_name=_("Customer"),
        on_delete=models.PROTECT,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        verbose_name=_("Vehicle"),
        on_delete=models.PROTECT,
    )
    parking_zone = models.ForeignKey(
        ParkingZone,
        verbose_name=_("Parking zone"),
        on_delete=models.PROTECT,
    )
    status = models.CharField(
        _("Status"),
        max_length=32,
        default=constants.ParkingPermitStatus.DRAFT.value,
        choices=[(tag.value, tag.value) for tag in constants.ParkingPermitStatus],
    )
    identifier = models.IntegerField(
        default=get_next_identifier, editable=False, unique=True, db_index=True
    )
    start_time = models.DateTimeField(_("Start time"), default=timezone.now)
    end_time = models.DateTimeField(_("End time"), blank=True, null=True)
    primary_vehicle = models.BooleanField(default=True)
    contract_type = models.CharField(
        _("Contract type"),
        max_length=16,
        default=constants.ContractType.OPEN_ENDED.value,
        choices=[(tag.value, tag.value) for tag in constants.ContractType],
    )
    start_type = models.CharField(
        _("Start type"),
        max_length=16,
        default=constants.StartType.IMMEDIATELY.value,
        choices=[(tag.value, tag.value) for tag in constants.StartType],
    )
    month_count = models.IntegerField(_("Month count"), default=1)

    order_id = models.CharField(max_length=50, blank=True, null=True)
    subscription_id = models.CharField(
        max_length=50, unique=True, blank=True, null=True
    )

    objects = ParkingPermitManager()

    class Meta:
        db_table = "parking_permit"
        verbose_name = _("Parking permit")
        verbose_name_plural = _("Parking permits")

    def __str__(self):
        return "%s" % self.identifier

    @property
    def consent_low_emission_accepted(self):
        return self.vehicle.consent_low_emission_accepted

    def get_prices(self):
        # TODO: account for different prices in different years
        monthly_price = self.parking_zone.resident_price
        month_count = self.month_count

        if self.contract_type == constants.ContractType.OPEN_ENDED.value:
            month_count = 1
        if not self.primary_vehicle:
            increase = decimal.Decimal(SECONDARY_VEHICLE_PRICE_INCREASE) / 100
            monthly_price += increase * monthly_price

        if self.vehicle.is_low_emission:
            discount = decimal.Decimal(LOW_EMISSION_DISCOUNT) / 100
            monthly_price -= discount * monthly_price

        return monthly_price * month_count, monthly_price

    @property
    def is_valid(self):
        return self.status == ParkingPermitStatus.VALID.value

    @property
    def is_open_ended(self):
        return self.contract_type == ContractType.OPEN_ENDED.value

    @property
    def is_fixed_period(self):
        return self.contract_type == ContractType.FIXED_PERIOD.value

    @property
    def can_end_immediately(self):
        now = timezone.now()
        return self.is_valid and (self.end_time is None or now < self.end_time)

    @property
    def can_end_after_current_period(self):
        return self.is_valid and (
            self.end_time is None or self.current_period_end_time < self.end_time
        )

    @property
    def months_used(self):
        now = timezone.now()
        diff_months = diff_months_ceil(self.start_time, now)
        if self.is_fixed_period:
            return min(self.month_count, diff_months)
        return diff_months

    @property
    def months_left(self):
        if self.is_open_ended:
            return None
        return self.month_count - self.months_used

    @property
    def current_period_end_time(self):
        return get_end_time(self.start_time, self.months_used)

    @property
    def has_refund(self):
        return hasattr(self, "refund")

    @property
    def monthly_price(self):
        # TODO: return different price for different permit types
        return self.parking_zone.resident_price

    @property
    def refund_amount(self):
        # TODO: account for different prices in different years
        return self.months_left * self.monthly_price

    def end_permit(self, end_type):
        if end_type == ParkingPermitEndType.AFTER_CURRENT_PERIOD.value:
            end_time = self.current_period_end_time
        else:
            end_time = timezone.now()

        if (
            self.primary_vehicle
            and self.customer.parkingpermit_set.active_after(end_time)
            .exclude(id=self.id)
            .exists()
        ):
            raise PermitCanNotBeEnded(
                _(
                    "Cannot close primary vehicle permit if an active secondary vehicle permit exists"
                )
            )

        self.end_time = end_time
        if end_type == ParkingPermitEndType.IMMEDIATELY.value:
            self.status = ParkingPermitStatus.CLOSED.value
        self.save()

    def create_refund(self, iban):
        if not self.is_fixed_period:
            raise RefundCanNotBeCreated(
                f"Refund cannot be created for {self.contract_type}"
            )
        return Refund.objects.create(
            permit=self, customer=self.customer, amount=self.refund_amount, iban=iban
        )

    def end_subscription(self):
        # TODO: end subscription
        pass

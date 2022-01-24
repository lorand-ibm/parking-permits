import decimal
import logging

import reversion
from dateutil.relativedelta import relativedelta
from django.contrib.gis.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..constants import (
    LOW_EMISSION_DISCOUNT,
    SECONDARY_VEHICLE_PRICE_INCREASE,
    ParkingPermitEndType,
)
from ..exceptions import PermitCanNotBeEnded, RefundCanNotBeCreated
from ..utils import diff_months_ceil, get_end_time
from .customer import Customer
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .parking_zone import ParkingZone
from .refund import Refund
from .vehicle import Vehicle

logger = logging.getLogger("db")


class ContractType(models.TextChoices):
    FIXED_PERIOD = "FIXED_PERIOD", _("Fixed period")
    OPEN_ENDED = "OPEN_ENDED", _("Open ended")


class ParkingPermitStartType(models.TextChoices):
    IMMEDIATELY = "IMMEDIATELY", _("Immediately")
    FROM = "FROM", _("From")


class ParkingPermitStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    ARRIVED = "ARRIVED", _("Arrived")
    PROCESSING = "PROCESSING", _("Processing")
    ACCEPTED = "ACCEPTED", _("Accepted")
    REJECTED = "REJECTED", _("Rejected")
    PAYMENT_IN_PROGRESS = "PAYMENT_IN_PROGRESS", _("Payment in progress")
    VALID = "VALID", _("Valid")
    CLOSED = "CLOSED", _("Closed")


def get_next_identifier():
    last = ParkingPermit.objects.order_by("-identifier").first()
    if not last:
        return 80000000
    return last.identifier + 1


class ParkingPermitManager(models.Manager):
    def active(self):
        active_status = [
            ParkingPermitStatus.VALID,
            ParkingPermitStatus.PAYMENT_IN_PROGRESS,
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
        choices=ParkingPermitStatus.choices,
        default=ParkingPermitStatus.DRAFT,
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
        choices=ContractType.choices,
        default=ContractType.OPEN_ENDED,
    )
    start_type = models.CharField(
        _("Start type"),
        max_length=16,
        choices=ParkingPermitStartType.choices,
        default=ParkingPermitStartType.IMMEDIATELY,
    )
    month_count = models.IntegerField(_("Month count"), default=1)
    order = models.ForeignKey(
        "Order",
        related_name="permits",
        verbose_name=_("Order"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    objects = ParkingPermitManager()

    class Meta:
        ordering = ["-identifier"]
        verbose_name = _("Parking permit")
        verbose_name_plural = _("Parking permits")

    def __str__(self):
        return "%s" % self.identifier

    @property
    def consent_low_emission_accepted(self):
        return self.vehicle.consent_low_emission_accepted

    def get_prices(self):
        # TODO: account for different prices in different years
        logger.error(
            "To be removed. This method is replaced by get_products_with_quantities"
        )
        monthly_price = self.parking_zone.resident_price
        month_count = self.month_count

        if self.contract_type == ContractType.OPEN_ENDED:
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
        return self.status == ParkingPermitStatus.VALID

    @property
    def is_open_ended(self):
        return self.contract_type == ContractType.OPEN_ENDED

    @property
    def is_fixed_period(self):
        return self.contract_type == ContractType.FIXED_PERIOD

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
    def current_period_start_time(self):
        return self.start_time + relativedelta(months=self.months_used - 1)

    @property
    def current_period_end_time(self):
        return get_end_time(self.start_time, self.months_used)

    @property
    def has_refund(self):
        return hasattr(self, "refund")

    @property
    def monthly_price(self):
        """
        Return the monthly price for current period

        Current monthly price is determined by the start date of current period
        """
        period_start_date = timezone.localdate(self.current_period_start_time)
        product = self.parking_zone.products.for_resident().get_for_date(
            period_start_date
        )
        is_secondary = not self.primary_vehicle
        return product.get_modified_unit_price(
            self.vehicle.is_low_emission, is_secondary
        )

    @property
    def refund_amount(self):
        # TODO: account for different prices in different years
        return self.months_left * self.monthly_price

    def end_permit(self, end_type):
        if end_type == ParkingPermitEndType.AFTER_CURRENT_PERIOD:
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
        if end_type == ParkingPermitEndType.IMMEDIATELY:
            self.status = ParkingPermitStatus.CLOSED
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

    def get_products_with_quantities(self):
        """Return a list of product and quantities for the permit"""
        # TODO: currently, company permit type is not available
        qs = self.parking_zone.products.for_resident()

        if self.is_open_ended:
            permit_start_date = timezone.localdate(self.start_time)
            product = qs.get_for_date(permit_start_date)
            return [(product, 1)]

        if self.is_fixed_period:
            permit_start_date = timezone.localdate(self.start_time)
            permit_end_date = timezone.localdate(self.end_time)
            return qs.get_products_with_quantities(permit_start_date, permit_end_date)

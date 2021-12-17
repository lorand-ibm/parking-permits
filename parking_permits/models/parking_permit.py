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
from ..exceptions import PermitCanNotBeEnded, ProductCatalogError, RefundCanNotBeCreated
from ..utils import diff_months_ceil, get_end_time
from .customer import Customer
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .parking_zone import ParkingZone
from .product import Product, ProductType
from .refund import Refund
from .vehicle import Vehicle

logger = logging.getLogger(__name__)


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
    order_id = models.CharField(max_length=50, blank=True)
    subscription_id = models.CharField(max_length=50, blank=True)

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
    def current_period_end_time(self):
        return get_end_time(self.start_time, self.months_used)

    @property
    def has_refund(self):
        return hasattr(self, "refund")

    @property
    def monthly_price(self):
        # TODO: return different price for different permit types
        price = self.parking_zone.resident_price
        if not self.primary_vehicle:
            price += price * decimal.Decimal(SECONDARY_VEHICLE_PRICE_INCREASE) / 100
        return price

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
        qs = Product.objects.filter(type=ProductType.RESIDENT)

        if self.is_open_ended:
            permit_start_date = timezone.localdate(self.start_time)
            try:
                product = qs.get(
                    zone=self.parking_zone,
                    start_date__lte=permit_start_date,
                    end_date__gte=permit_start_date,
                )
                return [(product, 1)]
            except Product.DoesNotExist:
                logger.error(f"Product does not exist for date {permit_start_date}")
                raise ProductCatalogError(
                    _("Product catalog error, please report to admin")
                )
            except Product.MultipleObjectsReturned:
                logger.error(
                    f"Products date range overlapping for date {permit_start_date}"
                )
                raise ProductCatalogError(
                    _("Product catalog error, please report to admin")
                )

        if self.is_fixed_period:
            permit_start_date = timezone.localdate(self.start_time)
            permit_end_date = timezone.localdate(self.end_time)
            query = Q(zone=self.parking_zone) & (
                Q(start_date__range=(permit_start_date, permit_end_date))
                | Q(end_date__range=(permit_start_date, permit_end_date))
            )
            # convert to list to enable minus indexing
            products = list(qs.filter(query).order_by("start_date"))
            # check product date range covers the whole duration of the permit
            if (
                permit_start_date < products[0].start_date
                or permit_end_date > products[-1].end_date
            ):
                logger.error("Products does not cover permit duration")
                raise ProductCatalogError(
                    _("Product catalog error, please report to admin")
                )

            products_with_quantities = [[product, 0] for product in products]

            # the price of the month is determined by the start date of month period
            period_starts = [
                permit_start_date + relativedelta(months=n)
                for n in range(self.month_count)
            ]
            product_index = 0
            period_index = 0
            while product_index < len(products) and period_index < len(period_starts):
                if period_starts[period_index] <= products[product_index].end_date:
                    products_with_quantities[product_index][1] += 1
                    period_index += 1
                else:
                    product_index += 1

            return products_with_quantities

import json
import logging
from decimal import Decimal

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from parking_permits.exceptions import CreateTalpaProductError, ProductCatalogError

from .mixins import TimestampedModelMixin, UserStampedModelMixin, UUIDPrimaryKeyMixin
from .parking_zone import ParkingZone

logger = logging.getLogger("db")


SECONDARY_VEHICLE_INCREASE_RATE = Decimal(0.5)


class ProductType(models.TextChoices):
    COMPANY = "COMPANY", _("Company")
    RESIDENT = "RESIDENT", _("Resident")


class Unit(models.TextChoices):
    MONTHLY = "MONTHLY", _("Monthly")
    PIECES = "PIECES", _("Pieces")


class ProductQuerySet(models.QuerySet):
    def for_resident(self):
        return self.filter(type=ProductType.RESIDENT)

    def for_company(self):
        return self.filter(type=ProductType.COMPANY)

    def get_for_date(self, dt):
        try:
            return self.get(start_date__lte=dt, end_date__gte=dt)
        except Product.DoesNotExist:
            logger.error(f"Product does not exist for date {dt}")
            raise ProductCatalogError(
                _("Product catalog error, please report to admin")
            )
        except Product.MultipleObjectsReturned:
            logger.error(f"Products date range overlapping for date {dt}")
            raise ProductCatalogError(
                _("Product catalog error, please report to admin")
            )

    def for_date_range(self, start_date, end_date):
        return self.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
        ).order_by("start_date")

    def get_products_with_quantities(self, start_date, end_date):
        # convert to list to enable minus indexing
        products = list(self.for_date_range(start_date, end_date))
        # check product date range covers the whole duration of the permit
        if start_date < products[0].start_date or end_date > products[-1].end_date:
            logger.error("Products does not cover permit duration")
            raise ProductCatalogError(
                _("Product catalog error, please report to admin")
            )

        products_with_quantities = [[product, 0] for product in products]

        # the price of the month is determined by the start date of month period
        product_index = 0
        period_start = start_date
        while product_index < len(products) and period_start < end_date:
            if period_start <= products[product_index].end_date:
                products_with_quantities[product_index][1] += 1
                period_start += relativedelta(months=1)
            else:
                product_index += 1

        return products_with_quantities


class Product(TimestampedModelMixin, UserStampedModelMixin, UUIDPrimaryKeyMixin):
    talpa_product_id = models.UUIDField(
        _("Talpa product id"),
        unique=True,
        editable=False,
        blank=True,
        null=True,
    )
    zone = models.ForeignKey(
        ParkingZone,
        verbose_name=_("zone"),
        related_name="products",
        on_delete=models.PROTECT,
    )
    type = models.CharField(
        _("Type"),
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.RESIDENT,
    )
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))
    unit_price = models.DecimalField(_("Unit price"), max_digits=6, decimal_places=2)
    unit = models.CharField(
        _("Unit"), max_length=50, choices=Unit.choices, default=Unit.MONTHLY
    )
    vat = models.DecimalField(_("VAT"), max_digits=6, decimal_places=4)
    low_emission_discount = models.DecimalField(
        _("Low emission discount"), max_digits=4, decimal_places=2
    )
    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name

    @property
    def secondary_vehicle_increase_rate(self):
        return SECONDARY_VEHICLE_INCREASE_RATE

    @property
    def vat_percentage(self):
        return self.vat * 100

    @vat_percentage.setter
    def vat_percentage(self, value):
        self.vat = value / 100

    @property
    def name(self):
        # the product name is the same for different languages
        # so no translation needed
        return f"Pysäköintialue {self.zone.name}"

    def get_modified_unit_price(self, is_low_emission, is_secondary):
        price = self.unit_price
        if is_low_emission:
            price -= price * self.low_emission_discount
        if is_secondary:
            price += price * self.secondary_vehicle_increase_rate
        return price

    def create_talpa_product(self):
        if self.talpa_product_id:
            logger.warning("Talpa product has been created already")
            return

        data = {
            "namespace": settings.NAMESPACE,
            "namespaceEntityId": str(self.id),
            "name": self.name,
        }
        headers = {
            "api-key": settings.TALPA_API_KEY,
            "Content-Type": "application/json",
        }
        response = requests.post(
            settings.TALPA_PRODUCT_EXPERIENCE_API,
            data=json.dumps(data),
            headers=headers,
        )
        if response.status_code == 201:
            logger.info("Talpa product created")
            data = response.json()
            self.talpa_product_id = data["productId"]
            self.save()
        else:
            logger.error(
                "Failed to create Talpa product. "
                f"Error: {response.status_code} {response.reason}. "
                f"Detail: {response.text}"
            )
            raise CreateTalpaProductError(
                "Cannot create Talpa Product. "
                f"Error: {response.status_code} {response.reason}."
            )

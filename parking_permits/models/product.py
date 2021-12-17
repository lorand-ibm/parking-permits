import logging

import requests
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from parking_permits.exceptions import CreateTalpaProductError

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .parking_zone import ParkingZone

logger = logging.getLogger(__name__)


class ProductType(models.TextChoices):
    COMPANY = "COMPANY", _("Company")
    RESIDENT = "RESIDENT", _("Resident")


class Unit(models.TextChoices):
    MONTHLY = "MONTHLY", _("Monthly")


class Product(TimestampedModelMixin, UUIDPrimaryKeyMixin):
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
    vat = models.DecimalField(_("VAT"), max_digits=4, decimal_places=2)
    low_emission_discount = models.DecimalField(
        _("Low emission discount"), max_digits=4, decimal_places=2
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name

    @property
    def vat_percentage(self):
        return self.vat * 100

    @property
    def name(self):
        # the product name is the same for different languages
        # so no translation needed
        return f"Pysäköintialue {self.zone.name}"

    def create_talpa_product(self):
        if self.talpa_product_id:
            logger.warning("Talpa product has been created already")
            return

        data = {
            "namespace": settings.NAMESPACE,
            "namespaceEntityId": self.id,
            "name": self.name,
        }
        headers = {
            "api-key": settings.TALPA_API_KEY,
            "Content-Type": "application/json",
        }
        response = requests.post(
            settings.TALPA_PRODUCT_EXPERIENCE_API, data=data, headers=headers
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

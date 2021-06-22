import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .constants import CATEGORIES, CONTRACT_TYPES, VEHICLE_TYPES
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


# TODO: Some of these fields should come directly from Helsinki profile User-model.
#  Check how to combine this model with Helsinki profile User-model.
class Customer(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    first_name = models.CharField(_("First name"), max_length=32)
    last_name = models.CharField(_("Last name"), max_length=32)
    national_id_number = models.CharField(
        _("National identification number"), max_length=16
    )
    primary_address = models.ForeignKey(
        "Address",
        verbose_name=_("Primary address"),
        on_delete=models.PROTECT,
        related_name="customers_primary_address",
    )
    other_address = models.ForeignKey(
        "Address",
        verbose_name=_("Other address"),
        on_delete=models.PROTECT,
        related_name="customers_other_address",
        blank=True,
        null=True,
    )
    email = models.CharField(_("Email"), max_length=128, blank=True, null=True)
    phone_number = models.CharField(
        _("Phone number"), max_length=32, blank=True, null=True
    )
    parking_zone = models.ForeignKey(
        "ParkingZone", verbose_name=_("Parking zone"), on_delete=models.PROTECT
    )
    consent_terms_of_use_accepted = models.BooleanField(null=False, default=False)
    consent_low_emission_accepted = models.BooleanField(null=False, default=False)

    class Meta:
        db_table = "customer"
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self):
        return "%s - %s %s" % (self.id, self.first_name, self.last_name)


class ParkingZone(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(_("Name"), max_length=128, blank=False, null=False)
    location = models.MultiPolygonField(
        _("Area (2D)"), srid=settings.SRID, blank=False, null=False
    )

    class Meta:
        db_table = "parking_zone"
        verbose_name = _("Parking zone")
        verbose_name_plural = _("Parking zones")

    def __str__(self):
        return "%s - %s" % (self.id, self.name)


class VehicleType(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    type = models.CharField(
        _("Type"), max_length=32, blank=False, null=False, choices=VEHICLE_TYPES
    )

    class Meta:
        db_table = "vehicle_type"
        verbose_name = _("Vehicle type")
        verbose_name_plural = _("Vehicle types")

    def __str__(self):
        return "%s - %s" % (self.id, self.type)


class LowEmissionCriteria(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    vehicle_type = models.ForeignKey(
        VehicleType,
        verbose_name=_("Vehicle type"),
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    emission_limit_nedc = models.IntegerField(
        _("Emission limit (NEDC)"), blank=True, null=True
    )
    emission_limit_wltp = models.IntegerField(
        _("Emission limit (WLTP)"), blank=True, null=True
    )
    start_date = models.DateField(_("Start date"), blank=False, null=False)
    end_date = models.DateField(_("End date"), blank=True, null=True)

    class Meta:
        db_table = "low_emission_criteria"
        verbose_name = _("Low-emission criteria")
        verbose_name_plural = _("Low-emission criterias")

    def __str__(self):
        return "%s - %s, NEDC: %s, WLTP: %s" % (
            self.id,
            self.vehicle_type,
            self.emission_limit_nedc,
            self.emission_limit_wltp,
        )


class Address(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    street_name = models.CharField(
        _("Street name"), max_length=128, blank=False, null=False
    )
    street_number = models.CharField(
        _("Street number"), max_length=128, blank=False, null=False
    )
    city = models.CharField(_("City"), max_length=128, blank=False, null=False)
    location = models.PointField(
        _("Location (2D)"), srid=settings.SRID, blank=False, null=False
    )

    class Meta:
        db_table = "address"
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return "%s - %s %s, %s" % (
            self.id,
            self.street_name,
            self.street_number,
            self.city,
        )


class Company(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(_("Company name"), max_length=128, blank=False, null=False)
    business_id = models.CharField(
        _("Business Id"), max_length=32, blank=False, null=False
    )
    address = models.ForeignKey(
        Address, verbose_name=_("Address"), on_delete=models.PROTECT
    )
    company_owner = models.ForeignKey(
        Customer, verbose_name=_("Company owner"), on_delete=models.PROTECT
    )

    class Meta:
        db_table = "company"
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return "%s - %s" % (self.id, self.name)


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
        choices=CATEGORIES,
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
    emission = models.IntegerField(_("Emission"), blank=False, null=False)
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


class DrivingClass(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    class_name = models.CharField(
        _("Driving class name"), max_length=32, blank=False, null=False
    )
    identifier = models.CharField(
        _("Driving class identifier"), max_length=32, blank=False, null=False
    )

    class Meta:
        db_table = "driving_class"
        verbose_name = _("Driving class")
        verbose_name_plural = _("Driving classes")

    def __str__(self):
        return "%s - %s - %s" % (self.id, self.class_name, self.identifier)


class DrivingLicence(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    customer = models.ForeignKey(
        Customer, verbose_name=_("Customer"), on_delete=models.PROTECT
    )
    driving_classes = models.ManyToManyField(DrivingClass)
    valid_start = models.DateTimeField(_("Valid start"))
    valid_end = models.DateTimeField(_("Valid end"))
    active = models.BooleanField(null=False, default=True)

    class Meta:
        db_table = "driving_licence"
        verbose_name = _("Driving licence")
        verbose_name_plural = _("Driving licences")

    def __str__(self):
        return "%s - %s, active: %s" % (self.id, self.customer, self.active)


class ContractType(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    contract_type = models.CharField(
        _("Contract type"),
        max_length=16,
        blank=False,
        null=False,
        choices=CONTRACT_TYPES,
    )
    month_count = models.IntegerField(_("Month count"), blank=True, null=True)

    class Meta:
        db_table = "contract_type"
        verbose_name = _("Contract type")
        verbose_name_plural = _("Contract types")

    def __str__(self):
        return "%s - %s, months: %s" % (self.id, self.contract_type, self.month_count)


class Product(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    shared_product_id = models.UUIDField(
        unique=True, editable=False, default=uuid.uuid4
    )
    name = models.CharField(_("Product name"), max_length=32, blank=False, null=False)

    class Meta:
        db_table = "product"
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name


class ProductPrice(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product price"),
        on_delete=models.PROTECT,
        related_name="prices",
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        _("Product price"), blank=False, null=False, max_digits=6, decimal_places=2
    )
    start_date = models.DateField(_("Start date"), blank=False, null=False)
    end_date = models.DateField(_("End date"), blank=True, null=True)

    class Meta:
        db_table = "price"
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")

    def __str__(self):
        return "%s %s - %s -> %s" % (
            self.id,
            self.start_date,
            self.end_date,
            str(self.price),
        )


class ParkingPermit(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    customer = models.ForeignKey(
        Customer,
        verbose_name=_("Customer"),
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        verbose_name=_("Vehicle"),
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    parking_zone = models.ForeignKey(
        ParkingZone,
        verbose_name=_("Parking zone"),
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    contract_type = models.ForeignKey(
        ContractType,
        verbose_name=_("Contract type"),
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    start_time = models.DateTimeField(_("Start time"), blank=False, null=False)
    end_time = models.DateTimeField(_("End time"), blank=True, null=True)

    class Meta:
        db_table = "parking_permit"
        verbose_name = _("Parking permit")
        verbose_name_plural = _("Parking permits")

    def __str__(self):
        return "%s - %s - %s - %s - %s - %s - %s" % (
            self.id,
            self.customer,
            self.vehicle,
            self.product,
            self.contract_type,
            self.start_time,
            self.end_time,
        )

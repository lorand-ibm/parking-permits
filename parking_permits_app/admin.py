from django.contrib.gis import admin

from parking_permits_app.models import (
    Address,
    Company,
    Customer,
    DrivingClass,
    DrivingLicence,
    LowEmissionCriteria,
    ParkingPermit,
    ParkingZone,
    Price,
    Vehicle,
    VehicleType,
)


@admin.register(Address)
class AddressAdmin(admin.OSMGeoAdmin):
    search_fields = ("street_name", "street_name_sv", "city", "city_sv")
    list_display = (
        "id",
        "street_name",
        "street_name_sv",
        "street_number",
        "postal_code",
        "city",
        "city_sv",
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ("name", "business_id")
    list_display = ("id", "name", "business_id", "address", "company_owner")
    list_select_related = ("address", "company_owner")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ("first_name", "last_name")
    list_display = ("__str__", "national_id_number", "email")

    def has_add_permission(self, request):
        return False


@admin.register(DrivingClass)
class DrivingClassAdmin(admin.ModelAdmin):
    list_display = ("class_name", "identifier")


@admin.register(DrivingLicence)
class DrivingLicenceAdmin(admin.ModelAdmin):
    search_fields = ("customer__first_name", "customer__last_name")
    list_display = ("id", "customer", "valid_start", "valid_end", "active")
    list_select_related = ("customer",)


@admin.register(LowEmissionCriteria)
class LowEmissionCriteriaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vehicle_type",
        "nedc_max_emission_limit",
        "wltp_max_emission_limit",
        "euro_min_class_limit",
        "start_date",
        "end_date",
    )
    list_select_related = ("vehicle_type",)


@admin.register(ParkingPermit)
class ParkingPermitAdmin(admin.ModelAdmin):
    search_fields = ("customer__first_name", "customer__last_name")
    list_display = (
        "identifier",
        "customer",
        "vehicle",
        "parking_zone",
        "status",
        "start_time",
        "end_time",
        "contract_type",
    )
    list_select_related = ("customer", "vehicle", "parking_zone")


@admin.register(ParkingZone)
class ParkingZoneAdmin(admin.OSMGeoAdmin):
    list_display = ("id", "name", "description", "description_sv", "shared_product_id")
    ordering = ("name",)


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ("id", "zone", "price", "start_date", "end_date")
    list_select_related = ("zone",)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    search_fields = ("registration_number", "manufacturer", "model")
    list_display = (
        "id",
        "registration_number",
        "manufacturer",
        "model",
        "owner",
        "holder",
    )
    list_select_related = ("owner", "holder")


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ("type",)

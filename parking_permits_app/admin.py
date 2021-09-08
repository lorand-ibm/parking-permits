from django.apps import apps
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

MODEL_ADMIN_ATTRIBUTES = {
    "ParkingZone": {
        "list_display": [
            "id",
            "name",
            "description",
            "description_sv",
            "shared_product_id",
        ],
        "ordering": ["name"],
        "search_fields": ["name"],
    },
    "Price": {
        "list_display": ["zone", "start_date", "end_date", "price"],
        "ordering": ["-start_date"],
    },
    "ParkingPermit": {
        "list_display": [
            "identifier",
            "customer",
            "vehicle",
            "parking_zone",
            "start_time",
            "end_time",
        ],
        "search_fields": ["identifier"],
        "ordering": ["-start_time"],
    },
}

all_models = apps.all_models["parking_permits_app"].values()

for model in all_models:
    model_admin = type(
        "OSMGeoAdmin",
        (OSMGeoAdmin,),
        MODEL_ADMIN_ATTRIBUTES.get(model.__name__, dict()),
    )
    admin.site.register(model, model_admin)

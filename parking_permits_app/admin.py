from django.apps import apps
from django.contrib import admin

MODEL_ADMIN_ATTRIBUTES = {
    "Product": {
        "list_display": ["name", "shared_product_id"],
        "ordering": ["name"],
        "search_fields": ["name"],
    },
    "ProductPrice": {
        "list_display": ["product", "start_date", "end_date", "price"],
        "ordering": ["-start_date"],
    },
}

all_models = apps.all_models["parking_permits_app"].values()

for model in all_models:
    model_admin = type(
        "ModelAdmin",
        (admin.ModelAdmin,),
        MODEL_ADMIN_ATTRIBUTES.get(model.__name__, dict()),
    )
    admin.site.register(model, model_admin)

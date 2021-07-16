from django.urls import path
from rest_framework.routers import DefaultRouter

from parking_permits_app import graphql, views

from .url_utils import versioned_url

router = DefaultRouter()
router.register(r"product", views.ProductViewSet, basename="product")

app_name = "parking_permits_app"
urlpatterns = [
    path("graphql/", graphql.view, name="graphql"),
    path(
        "api/talpa/resolve-availability/",
        views.TalpaResolveAvailability.as_view(),
        name="talpa-availability",
    ),
    path(
        "api/talpa/resolve-price/",
        views.TalpaResolvePrice.as_view(),
        name="talpa-price",
    ),
    versioned_url("v1", router.urls),
]

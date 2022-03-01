from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="Parking permits API",
        default_version="v1",
        description="Parking permits API",
        terms_of_service="https://www.hel.fi/helsinki/fi/kartat-ja-liikenne/pysakointi/vahapaastoisten_alennus",
        contact=openapi.Contact(email="permits@hel.fi"),
    ),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/admin/")),
    path("", include("parking_permits.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

from django.urls import path

from parking_permits_app import graphql

urlpatterns = [
    path("graphql/", graphql.view, name="graphql"),
]

from rest_framework import serializers

from .models import Product, ProductPrice


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = [
            "id",
            "price",
            "start_date",
            "end_date",
        ]
        read_only_fields = [
            "id",
        ]


class ProductSerializer(serializers.ModelSerializer):
    prices = ProductPriceSerializer(read_only=True, many=True)
    namespace = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "shared_product_id",
            "name",
            "prices",
            "namespace",
            "description",
        ]
        read_only_fields = [
            "id",
            "shared_product_id",
        ]

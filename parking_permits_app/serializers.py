from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "shared_product_id",
            "name",
            "price",
            "start_date",
            "end_date",
        ]
        read_only_fields = [
            "id",
            "shared_product_id",
        ]

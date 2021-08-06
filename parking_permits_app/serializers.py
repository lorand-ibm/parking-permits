from rest_framework import serializers

from .models import ParkingZone, Price


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = [
            "id",
            "price",
            "start_date",
            "end_date",
        ]
        read_only_fields = [
            "id",
        ]


class ParkingZoneSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(read_only=True, many=True)
    namespace = serializers.ReadOnlyField()

    class Meta:
        model = ParkingZone
        fields = [
            "id",
            "shared_product_id",
            "name",
            "prices",
            "namespace",
        ]
        read_only_fields = [
            "id",
            "shared_product_id",
        ]

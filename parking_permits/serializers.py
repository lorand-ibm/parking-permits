from rest_framework import serializers


class MetaItemSerializer(serializers.Serializer):
    key = serializers.CharField(help_text="Meta id")
    value = serializers.CharField(help_text="Meta value")


class OrderItemSerializer(serializers.Serializer):
    orderItemId = serializers.CharField(help_text="Order item id")
    meta = MetaItemSerializer(many=True)


class RightOfPurchaseSerializer(serializers.Serializer):
    orderId = serializers.CharField(help_text="Id of a generated order")
    namespace = serializers.CharField(help_text="Namespace used by talpa")
    orderItem = OrderItemSerializer()


class RightOfPurchaseResponseSerializer(serializers.Serializer):
    errorMessage = serializers.CharField(help_text="Error if exists", default="")
    rightOfPurchase = serializers.BooleanField(help_text="Has rights to purchase")
    userId = serializers.CharField(help_text="User id")
    orderId = serializers.CharField(help_text="Order id")
    orderItemId = serializers.CharField(help_text="Order item id")


class OrderSerializer(serializers.Serializer):
    orderId = serializers.CharField(help_text="Id of a generated order")
    eventType = serializers.ChoiceField(
        help_text="Event types", choices=["PAYMENT_PAID"], default="PAYMENT_PAID"
    )


class ResolveAvailabilitySerializer(serializers.Serializer):
    productId = serializers.CharField(help_text="Shared product id")


class ResolveAvailabilityResponseSerializer(serializers.Serializer):
    productId = serializers.CharField(help_text="Shared product id")
    value = serializers.BooleanField(default=True)


class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Success or error message")

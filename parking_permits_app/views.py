from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Product, Vehicle
from .permissions import ReadOnly
from .pricing.engine import calculate_cart_item_total_price
from .serializers import ProductSerializer
from .services import talpa


class TalpaResolveAvailability(APIView):
    def post(self, request, format=None):
        shared_product_id = request.data.get("productId")

        response = talpa.resolve_availability_response(
            product_id=shared_product_id, availability=True
        )

        return Response(response)


class TalpaResolvePrice(APIView):
    def post(self, request, format=None):
        shared_product_id = request.data.get("productId")
        item_quantity = request.data.get("quantity")
        vehicle_id = talpa.get_meta_value(request.data.get("meta"), "vehicleId")

        if vehicle_id is None:
            return Response(
                {
                    "message": "No vehicleId key available in meta list of key-value pairs"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
            product = Product.objects.get(shared_product_id=shared_product_id)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        total_price = calculate_cart_item_total_price(
            item_price=product.get_current_price(),
            item_quantity=item_quantity,
            vehicle_is_secondary=vehicle.primary_vehicle is False,
            vehicle_is_low_emission=vehicle.is_low_emission(),
        )

        response = talpa.resolve_price_response(
            product_id=shared_product_id, total_price=total_price
        )

        return Response(response)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ReadOnly]

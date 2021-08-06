from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Customer, ParkingZone, Vehicle
from .permissions import ReadOnly
from .pricing.engine import calculate_cart_item_total_price
from .serializers import ParkingZoneSerializer
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
            zone = ParkingZone.objects.get(shared_product_id=shared_product_id)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        total_price = calculate_cart_item_total_price(
            item_price=zone.get_current_price(),
            item_quantity=item_quantity,
            vehicle_is_secondary=vehicle.primary_vehicle is False,
            vehicle_is_low_emission=vehicle.is_low_emission(),
        )

        response = talpa.resolve_price_response(
            product_id=shared_product_id, total_price=total_price
        )

        return Response(response)


class TalpaResolveRightOfPurchase(APIView):
    def post(self, request, format=None):
        shared_product_id = request.data.get("productId")
        profile_id = talpa.get_meta_value(request.data.get("meta"), "profileId")
        vehicle_id = talpa.get_meta_value(request.data.get("meta"), "vehicleId")

        try:
            customer = Customer.objects.get(pk=profile_id)
            vehicle = Vehicle.objects.get(pk=vehicle_id)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        right_of_purchase = (
            customer.has_valid_address_within_zone()
            and customer.is_owner_or_holder_of_vehicle(vehicle)
            and customer.driving_licence.is_valid_for_vehicle(vehicle)
            and not vehicle.is_due_for_inspection()
        )

        response = talpa.resolve_right_of_purchase_response(
            product_id=shared_product_id,
            right_of_purchase=right_of_purchase,
        )

        return Response(response)


class ParkingZoneViewSet(ModelViewSet):
    queryset = ParkingZone.objects.all()
    serializer_class = ParkingZoneSerializer
    permission_classes = [ReadOnly]

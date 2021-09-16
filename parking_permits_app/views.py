import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import ParkingPermit, ParkingZone
from .permissions import ReadOnly
from .serializers import ParkingZoneSerializer
from .services import talpa

logger = logging.getLogger(__name__)


class TalpaResolveAvailability(APIView):
    def post(self, request, format=None):
        shared_product_id = request.data.get("productId")

        response = talpa.resolve_availability_response(
            product_id=shared_product_id, availability=True
        )

        return Response(response)


class TalpaResolvePrice(APIView):
    def post(self, request, format=None):
        permit_id = talpa.get_meta_value(request.data.get("meta"), "permitId")

        if permit_id is None:
            return Response(
                {
                    "message": "No permitId key available in meta list of key-value pairs"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            permit = ParkingPermit.objects.get(pk=permit_id)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response = talpa.resolve_price_response(total_price=permit.get_total_price())

        return Response(response)


class TalpaResolveRightOfPurchase(APIView):
    def post(self, request, format=None):
        shared_product_id = request.data.get("productId")
        permit_id = talpa.get_meta_value(request.data.get("meta"), "permitId")

        try:
            permit = ParkingPermit.objects.get(pk=permit_id)
            customer = permit.customer
            vehicle = permit.vehicle
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        right_of_purchase = (
            customer.is_owner_or_holder_of_vehicle(vehicle)
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


class OrderView(APIView):
    def post(self, request, format=None):
        logger.info("Order received.", request.data)

        return Response({"message": "Order received"}, status=200)

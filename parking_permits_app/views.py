import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ParkingPermit
from .services import talpa

logger = logging.getLogger(__name__)


class TalpaResolveAvailability(APIView):
    def post(self, request, format=None):
        shared_product_id = request.data.get("productId")
        res = {"product_id": shared_product_id, "value": True}
        return Response(talpa.snake_to_camel_dict(res))


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
        total_price, monthly_price = permit.get_prices()
        response = talpa.resolve_price_response(total_price, monthly_price)

        return Response(talpa.snake_to_camel_dict(response))


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
        res = {"product_id": shared_product_id, "value": right_of_purchase}
        return Response(talpa.snake_to_camel_dict(res))


class OrderView(APIView):
    def post(self, request, format=None):
        logger.info("Order received.", request.data)

        return Response({"message": "Order received"}, status=200)

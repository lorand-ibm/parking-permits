import json
import logging

from django.conf import settings
from django.db import transaction
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from helsinki_gdpr.views import DeletionNotAllowed, DryRunSerializer, GDPRAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Customer, Order
from .models.common import SourceSystem
from .models.order import OrderItem, OrderStatus
from .models.parking_permit import ParkingPermitStatus
from .serializers import (
    MessageResponseSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ResolveAvailabilityResponseSerializer,
    ResolveAvailabilitySerializer,
    RightOfPurchaseResponseSerializer,
    RightOfPurchaseSerializer,
)
from .services import talpa

logger = logging.getLogger("db")


class TalpaResolveAvailability(APIView):
    @swagger_auto_schema(
        operation_description="Resolve product availability.",
        request_body=ResolveAvailabilitySerializer,
        responses={
            200: openapi.Response(
                "Product is always available for purchase.",
                ResolveAvailabilityResponseSerializer,
            )
        },
        tags=["ResolveAvailability"],
    )
    def post(self, request, format=None):
        shared_product_id = request.data.get("productId")
        res = {"product_id": shared_product_id, "value": True}
        return Response(talpa.snake_to_camel_dict(res))


class TalpaResolvePrice(APIView):
    @swagger_auto_schema(
        operation_description="Resolve price of product from an order item.",
        request_body=OrderItemSerializer,
        responses={
            200: openapi.Response(
                "Right of purchase response", MessageResponseSerializer
            )
        },
        tags=["ResolvePrice"],
    )
    def post(self, request, format=None):
        order_item_id = request.data.get("orderItem").get("orderItemId")

        if order_item_id is None:
            return Response(
                {"message": "No orderItemId is found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order_item = OrderItem.objects.get(talpa_order_item_id=order_item_id)
            price = order_item.payment_unit_price
            vat = order_item.vat
            price_vat = price * vat
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            talpa.snake_to_camel_dict(
                {
                    "row_price_net": float(price - price_vat),
                    "row_price_vat": float(price_vat),
                    "row_price_total": float(price),
                    "price_net": float(price - price_vat),
                    "price_vat": float(price_vat),
                    "price_gross": float(price),
                    "vat_percentage": float(vat * 100),
                }
            )
        )


class TalpaResolveRightOfPurchase(APIView):
    @swagger_auto_schema(
        operation_description="Used as an webhook by Talpa in order to send an order notification.",
        request_body=RightOfPurchaseSerializer,
        responses={
            200: openapi.Response(
                "Right of purchase response", RightOfPurchaseResponseSerializer
            )
        },
        tags=["RightOfPurchase"],
    )
    def post(self, request):
        user_id = request.data.get("userId")
        order_id = request.data.get("orderId")
        order_item_id = request.data.get("orderItem").get("orderItemId")

        try:
            order_item = OrderItem.objects.get(talpa_order_item_id=order_item_id)
            customer = order_item.permit.customer
            vehicle = order_item.permit.vehicle
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        right_of_purchase = (
            customer.is_owner_or_holder_of_vehicle(vehicle)
            and customer.driving_licence.is_valid_for_vehicle(vehicle)
            and not vehicle.is_due_for_inspection()
        )
        res = {
            "error_message": "",
            "right_of_purchase": right_of_purchase,
            "order_id": order_id,
            "user_id": user_id,
            "order_item_id": order_item_id,
        }
        return Response(talpa.snake_to_camel_dict(res))


class OrderView(APIView):
    @swagger_auto_schema(
        operation_description="Used as an webhook by Talpa in order to send an order notification.",
        request_body=OrderSerializer,
        security=[],
        responses={
            200: openapi.Response("Order received response", MessageResponseSerializer)
        },
        tags=["Order"],
    )
    @transaction.atomic
    def post(self, request, format=None):
        logger.info(f"Order received. Data = {json.dumps(request.data)}")
        talpa_order_id = request.data.get("orderId")
        event_type = request.data.get("eventType")
        if not talpa_order_id:
            logger.error("Talpa order id is missing from request data")
            return Response({"message": "No order id is provided"}, status=400)

        if event_type == "PAYMENT_PAID":
            order = Order.objects.get(talpa_order_id=talpa_order_id)
            order.status = OrderStatus.CONFIRMED
            order.save()
            for permit in order.permits.all():
                permit.status = ParkingPermitStatus.VALID
                permit.save()
                if not settings.DEBUG:
                    permit.create_parkkihubi_permit()

        logger.info(f"{order} is confirmed and order permits are set to VALID ")
        return Response({"message": "Order received"}, status=200)


class ParkingPermitsGDPRAPIView(GDPRAPIView):
    def get_object(self) -> Customer:
        try:
            customer = Customer.objects.get(
                source_system=SourceSystem.HELSINKI_PROFILE, source_id=self.kwargs["id"]
            )
        except Customer.DoesNotExist:
            raise Http404
        else:
            self.check_object_permissions(self.request, customer)
            return customer

    def _delete(self):
        customer = self.get_object()
        if not customer.can_be_deleted:
            raise DeletionNotAllowed()
        customer.delete_all_data()

    def delete(self, request, *args, **kwargs):
        dry_run_serializer = DryRunSerializer(data=request.data)
        dry_run_serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self._delete()
            if dry_run_serializer.data["dry_run"]:
                transaction.set_rollback(True)
        return Response(status=status.HTTP_204_NO_CONTENT)

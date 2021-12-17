import logging

import requests
from django.conf import settings
from django.utils.translation import gettext as _

from parking_permits.exceptions import OrderCreationFailed
from parking_permits.models.order import OrderType

logger = logging.getLogger(__name__)


class TalpaOrderManager:
    url = settings.TALPA_ORDER_EXPERIENCE_API
    headers = {
        "api-key": settings.TALPA_API_KEY,
        "namespace": settings.NAMESPACE,
        "Content-type": "application/json",
    }

    @classmethod
    def _create_item_data(cls, order, order_item):
        item = {
            "productId": order_item.product.talpa_product_id,
            "productName": order_item.product.name,
            "unit": "kk",
            "rowPriceNet": order_item.unit_price_net,
            "rowPriceVat": order_item.unit_price_vat,
            "rowPriceTotal": order_item.unit_price,
            "priceNet": order_item.total_price_net,
            "priceVat": order_item.total_price_vat,
            "priceGross": order_item.total_price,
            "vatPercentage": order_item.vat_percentage,
            "meta": [{"key": "vehicle", "value": str(order_item.permit.vehicle)}],
        }
        if order.type == OrderType.SUBSCRIPTION:
            item.update(
                {
                    "period_unit": "monthly",
                    "period_frequency": "1",
                }
            )
        return item

    @classmethod
    def _create_order_data(cls, order):
        order_items = order.order_items.all().select_related("product", "permit")
        items = [cls._create_item_data(order, order_item) for order_item in order_items]
        return {
            "namespace": settings.NAMESPACE,
            "user": str(order.customer.id),
            "priceNet": order.total_price_net,
            "priceVat": order.total_price_vat,
            "priceTotal": order.total_price,
            "items": items,
        }

    @classmethod
    def send_to_talpa(cls, order):
        order_data = cls._create_order_data(order)
        response = requests.post(cls.url, order_data, headers=cls.headers)
        if response.status_code >= 300:
            logger.error(
                f"Create talpa order failed for order {order}. Error: {response.text}"
            )
            raise OrderCreationFailed(_("Failed to create the order"))

        response_data = response.json()
        return response_data["checkoutUrl"]

import decimal
import json

import requests
from django.conf import settings

from parking_permits.constants import VAT_PERCENTAGE
from parking_permits.exceptions import OrderCreationFailed
from parking_permits.models import ParkingPermit
from parking_permits.models.parking_permit import ContractType, ParkingPermitStatus


def get_meta_value(meta_pair_list, meta_pair_key):
    return next(
        (
            meta_pair.get("value")
            for meta_pair in meta_pair_list
            if meta_pair.get("key") == meta_pair_key
        ),
        None,
    )


def resolve_price_response(total_price=0, monthly_price=0):
    price_vat = decimal.Decimal(VAT_PERCENTAGE) / 100 * total_price
    row_price_vat = decimal.Decimal(VAT_PERCENTAGE) / 100 * monthly_price
    return {
        "row_price_net": float(total_price - price_vat),
        "row_price_vat": float(price_vat),
        "row_price_total": float(total_price),
        "price_net": float(monthly_price - row_price_vat),
        "price_vat": float(row_price_vat),
        "price_gross": float(monthly_price),
        "vat_percentage": float(VAT_PERCENTAGE),
    }


def snake_to_camel_dict(dictionary):
    res = dict()
    for key in dictionary.keys():
        if isinstance(dictionary[key], dict):
            res[camel_str(key)] = snake_to_camel_dict(dictionary[key])
        elif isinstance(dictionary[key], list):
            res[camel_str(key)] = [snake_to_camel_dict(val) for val in dictionary[key]]
        else:
            res[camel_str(key)] = dictionary[key]
    return res


def camel_str(snake_str):
    first, *others = snake_str.split("_")
    return "".join([first.lower(), *map(str.title, others)])


def create_talpa_order(customer):
    data = {
        "customer": {
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
        },
        "items": [],
    }
    permits = ParkingPermit.objects.filter(
        customer=customer, status=ParkingPermitStatus.DRAFT
    )
    address = (
        customer.primary_address
        if permits.first().parking_zone == customer.primary_address.zone
        else customer.other_address
    )

    for permit in permits:
        total_price, monthly_price = permit.get_prices()
        month_count = permit.month_count
        open_ended_fields = {
            "period_unit": "monthly",
            "period_frequency": "1",
        }
        order_line_data = {
            "quantity": 1
            if permit.contract_type == ContractType.OPEN_ENDED
            else month_count,
            "product_id": str(address.zone.shared_product_id),
            "product_name": f"{address.zone.name} ({permit.vehicle.registration_number})",
            "unit": "kk",
            "meta": [{"key": "permitId", "value": str(permit.id)}],
        }
        order_line_data.update(resolve_price_response(total_price, monthly_price))
        if permit.contract_type == ContractType.OPEN_ENDED:
            order_line_data.update(open_ended_fields)
        data["items"].append(order_line_data)

    data.update(
        {
            "namespace": settings.NAMESPACE,
            "user": str(customer.id),
            "price_net": float(sum([item["price_net"] for item in data["items"]])),
            "price_vat": float(sum([item["price_vat"] for item in data["items"]])),
            "price_total": float(sum([item["price_gross"] for item in data["items"]])),
        }
    )

    headers = {
        "api-key": settings.TALPA_API_KEY,
        "namespace": settings.NAMESPACE,
        "Content-type": "application/json",
    }
    url = f"{settings.TALPA_ORDER_EXPERIENCE_API}"
    result = requests.post(
        url=url, data=json.dumps(snake_to_camel_dict(data)), headers=headers
    )
    if result.status_code >= 300:
        raise OrderCreationFailed(
            "Failed to create talpa order: {}".format(result.text)
        )
    return json.loads(result.text)

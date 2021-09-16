import decimal

from parking_permits_app.constants import VAT_PERCENTAGE


def get_meta_value(meta_pair_list, meta_pair_key):
    return next(
        (
            meta_pair.get("value")
            for meta_pair in meta_pair_list
            if meta_pair.get("key") == meta_pair_key
        ),
        None,
    )


def resolve_price_response(total_price=0):
    vat = decimal.Decimal(VAT_PERCENTAGE) / 100 * total_price
    return {
        "priceNet": total_price - vat,
        "priceVat": vat,
        "priceGross": total_price,
        "vatPercentage": VAT_PERCENTAGE,
    }


def resolve_availability_response(product_id=None, availability=None):
    return {
        "productId": product_id,
        "value": availability,
    }


def resolve_right_of_purchase_response(product_id=None, right_of_purchase=None):
    return {
        "productId": product_id,
        "value": right_of_purchase,
    }

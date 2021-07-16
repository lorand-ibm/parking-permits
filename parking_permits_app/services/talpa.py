from parking_permits_app.constants import VAT_PERCENTAGE
from parking_permits_app.pricing.value_added_tax import calculate_price_without_vat


def get_meta_value(meta_pair_list, meta_pair_key):
    return next(
        (
            meta_pair.get("value")
            for meta_pair in meta_pair_list
            if meta_pair.get("key") == meta_pair_key
        ),
        None,
    )


def resolve_price_response(product_id=None, total_price=None):
    return {
        "productId": product_id,
        "netValue": calculate_price_without_vat(total_price),
        "vatPercentage": VAT_PERCENTAGE,
        "grossValue": total_price,
        "vatValue": total_price - calculate_price_without_vat(total_price),
    }

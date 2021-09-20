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
        "price_net": total_price - vat,
        "price_vat": vat,
        "price_gross": total_price,
        "vat_percentage": VAT_PERCENTAGE,
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


def snake_to_camel_dict(dictionary):
    res = dict()
    for key in dictionary.keys():
        if isinstance(dictionary[key], dict):
            res[camel_str(key)] = snake_to_camel_dict(dictionary[key])
        else:
            res[camel_str(key)] = dictionary[key]
    return res


def camel_str(snake_str):
    first, *others = snake_str.split("_")
    return "".join([first.lower(), *map(str.title, others)])

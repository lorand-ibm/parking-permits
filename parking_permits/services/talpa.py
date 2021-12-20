import decimal

from parking_permits.constants import VAT_PERCENTAGE


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

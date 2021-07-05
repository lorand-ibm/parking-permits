from parking_permits_app.pricing.low_emission import (
    apply_low_emission_discount,
    is_low_emission,
)
from parking_permits_app.pricing.secondary_vehicle import (
    apply_secondary_vehicle_price_increase,
)


def calculate_cart_item_total_price(
    item_price=0,
    item_quantity=0,
    vehicle_is_secondary=False,
    euro_class=None,
    euro_class_min_limit=None,
    nedc_emission=None,
    nedc_emission_max_limit=None,
    wltp_emission=None,
    wltp_emission_max_limit=None,
):

    vehicle_is_low_emission = is_low_emission(
        euro_class=euro_class,
        euro_class_min_limit=euro_class_min_limit,
        nedc_emission=nedc_emission,
        nedc_emission_max_limit=nedc_emission_max_limit,
        wltp_emission=wltp_emission,
        wltp_emission_max_limit=wltp_emission_max_limit,
    )

    total_price = item_price * item_quantity

    if vehicle_is_secondary:
        total_price = apply_secondary_vehicle_price_increase(price=total_price)

    if vehicle_is_low_emission:
        total_price = apply_low_emission_discount(price=total_price)

    return total_price

from parking_permits_app.pricing.low_emission import apply_low_emission_discount
from parking_permits_app.pricing.secondary_vehicle import (
    apply_secondary_vehicle_price_increase,
)


def calculate_cart_item_total_price(
    item_price=0,
    item_quantity=0,
    vehicle_is_secondary=False,
    vehicle_is_low_emission=False,
):
    total_price = item_price * item_quantity

    if vehicle_is_secondary:
        total_price = apply_secondary_vehicle_price_increase(price=total_price)

    if vehicle_is_low_emission:
        total_price = apply_low_emission_discount(price=total_price)

    return total_price

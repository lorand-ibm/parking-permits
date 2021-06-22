from parking_permits_app.constants import SECONDARY_VEHICLE_PRICE_INCREASE


def apply_secondary_vehicle_price_increase(price=None):
    return price + (price / 100) * SECONDARY_VEHICLE_PRICE_INCREASE

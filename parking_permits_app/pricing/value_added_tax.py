from decimal import Decimal

from parking_permits_app.constants import VAT_PERCENTAGE


def calculate_price_without_vat(price_with_vat):
    vat_multiplier = Decimal("1") + (Decimal(VAT_PERCENTAGE) / Decimal("100"))

    price_without_vat = price_with_vat / vat_multiplier

    return round(price_without_vat, 2)

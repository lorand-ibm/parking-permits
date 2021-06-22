from decimal import Decimal

import pytest

from parking_permits_app.pricing.secondary_vehicle import (
    apply_secondary_vehicle_price_increase,
)


@pytest.mark.parametrize(
    "price, price_after_increase",
    [
        (Decimal("50"), Decimal("75")),
        (Decimal("10"), Decimal("15")),
        (Decimal("21"), Decimal("31.5")),
        (Decimal("0"), Decimal("0")),
        (Decimal("36.5"), Decimal("54.75")),
    ],
)
def test_apply_secondary_vehicle_price_increase_function_returns_correct_price(
    price, price_after_increase
):
    assert apply_secondary_vehicle_price_increase(price=price) == price_after_increase

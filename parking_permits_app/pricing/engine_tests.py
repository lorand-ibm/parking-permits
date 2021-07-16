from decimal import Decimal

import pytest

from parking_permits_app.pricing.engine import calculate_cart_item_total_price

PRIMARY_VEHICLE_HIGH_EMISSION = (
    Decimal("30"),
    3,
    False,
    False,
    Decimal("90"),
)

PRIMARY_VEHICLE_LOW_EMISSION = (
    Decimal("30"),
    3,
    False,
    True,
    Decimal("45"),
)

SECONDARY_VEHICLE_HIGH_EMISSION = (
    Decimal("30"),
    10,
    True,
    False,
    Decimal("450"),
)

SECONDARY_VEHICLE_LOW_EMISSION = (
    Decimal("30"),
    10,
    True,
    True,
    Decimal("225"),
)


@pytest.mark.parametrize(
    "item_price,"
    "item_quantity,"
    "vehicle_is_secondary,"
    "vehicle_is_low_emission,"
    "result,",
    [
        PRIMARY_VEHICLE_HIGH_EMISSION,
        PRIMARY_VEHICLE_LOW_EMISSION,
        SECONDARY_VEHICLE_HIGH_EMISSION,
        SECONDARY_VEHICLE_LOW_EMISSION,
    ],
)
def test_calculate_cart_item_total_price_function_returns_correct_result(
    item_price,
    item_quantity,
    vehicle_is_secondary,
    vehicle_is_low_emission,
    result,
):
    assert (
        calculate_cart_item_total_price(
            item_price=item_price,
            item_quantity=item_quantity,
            vehicle_is_secondary=vehicle_is_secondary,
            vehicle_is_low_emission=vehicle_is_low_emission,
        )
        == result
    )

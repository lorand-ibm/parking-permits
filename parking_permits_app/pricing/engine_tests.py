from decimal import Decimal

import pytest

from parking_permits_app.pricing.engine import calculate_cart_item_total_price

PRIMARY_VEHICLE_HIGH_EMISSION = (
    Decimal("30"),
    3,
    False,
    5,
    6,
    None,
    None,
    None,
    None,
    Decimal("90"),
)

PRIMARY_VEHICLE_LOW_EMISSION = (
    Decimal("30"),
    3,
    False,
    6,
    6,
    None,
    None,
    120,
    126,
    Decimal("45"),
)

SECONDARY_VEHICLE_HIGH_EMISSION = (
    Decimal("30"),
    10,
    True,
    5,
    6,
    None,
    None,
    None,
    None,
    Decimal("450"),
)

SECONDARY_VEHICLE_LOW_EMISSION = (
    Decimal("30"),
    10,
    True,
    6,
    6,
    None,
    None,
    120,
    126,
    Decimal("225"),
)


@pytest.mark.parametrize(
    "item_price,"
    "item_quantity,"
    "vehicle_is_secondary,"
    "euro_emission,"
    "euro_emission_min_limit,"
    "nedc_emission,"
    "nedc_emission_max_limit,"
    "wltp_emission,"
    "wltp_emission_max_limit,"
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
    euro_emission,
    euro_emission_min_limit,
    nedc_emission,
    nedc_emission_max_limit,
    wltp_emission,
    wltp_emission_max_limit,
    result,
):
    assert (
        calculate_cart_item_total_price(
            item_price=item_price,
            item_quantity=item_quantity,
            vehicle_is_secondary=vehicle_is_secondary,
            euro_emission=euro_emission,
            euro_emission_min_limit=euro_emission_min_limit,
            nedc_emission=nedc_emission,
            nedc_emission_max_limit=nedc_emission_max_limit,
            wltp_emission=wltp_emission,
            wltp_emission_max_limit=wltp_emission_max_limit,
        )
        == result
    )

from decimal import Decimal

import pytest

from parking_permits_app.pricing.low_emission import (
    apply_low_emission_discount,
    is_low_emission,
)


@pytest.mark.parametrize(
    "euro_class,"
    "euro_class_min_limit,"
    "nedc_emission,"
    "nedc_emission_max_limit,"
    "wltp_emission,"
    "wltp_emission_max_limit,"
    "result,",
    [
        (None, 6, 50, 95, 120, 126, False),
        (6, 6, None, 95, 120, 126, True),
        (6, 6, 50, 95, None, 126, True),
        (6, 6, None, 95, None, 126, False),
        (5, 6, 50, 95, 120, 126, False),
        (6, 6, 100, 95, 120, 126, True),
        (6, 6, 50, 95, 130, 126, True),
        (6, 6, 50, 95, 120, 126, True),
        (5, 6, 40, 50, 65, 70, False),
        (6, 6, 100, 50, 65, 70, True),
        (6, 6, 40, 50, 130, 70, True),
        (6, 6, 40, 50, 65, 70, True),
        (5, 6, 130, 150, 170, 180, False),
        (6, 6, 200, 150, 170, 180, True),
        (6, 6, 130, 150, 220, 180, True),
        (6, 6, 130, 150, 170, 180, True),
    ],
)
def test_is_low_emission_function_returns_correct_result(
    euro_class,
    euro_class_min_limit,
    nedc_emission,
    nedc_emission_max_limit,
    wltp_emission,
    wltp_emission_max_limit,
    result,
):
    assert (
        is_low_emission(
            euro_class=euro_class,
            euro_class_min_limit=euro_class_min_limit,
            nedc_emission=nedc_emission,
            nedc_emission_max_limit=nedc_emission_max_limit,
            wltp_emission=wltp_emission,
            wltp_emission_max_limit=wltp_emission_max_limit,
        )
        == result
    )


@pytest.mark.parametrize(
    "price, price_after_discount",
    [
        (Decimal("50"), Decimal("25")),
        (Decimal("10"), Decimal("5")),
        (Decimal("21"), Decimal("10.5")),
        (Decimal("0"), Decimal("0")),
        (Decimal("36.5"), Decimal("18.25")),
    ],
)
def test_apply_low_emission_discount_function_returns_correct_price(
    price, price_after_discount
):
    assert apply_low_emission_discount(price=price) == price_after_discount

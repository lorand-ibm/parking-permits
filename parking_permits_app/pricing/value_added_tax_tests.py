from decimal import Decimal

import pytest

from parking_permits_app.pricing.value_added_tax import calculate_price_without_vat


@pytest.mark.parametrize(
    "price_with_vat, price_without_vat",
    [
        (Decimal("124"), Decimal("100")),
        (Decimal("60"), Decimal("48.39")),
        (Decimal("10000"), Decimal("8064.52")),
        (Decimal("32.75"), Decimal("26.41")),
        (Decimal("0"), Decimal("0")),
    ],
)
def test_calculate_price_without_vat_function_returns_correct_result(
    price_with_vat, price_without_vat
):
    assert calculate_price_without_vat(price_with_vat) == price_without_vat

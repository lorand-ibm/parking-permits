import datetime

import pytest
from django.utils.timezone import utc


@pytest.mark.django_db
def test_product_prices(product_factory, product_price_factory):
    product = product_factory()
    product_price = product_price_factory(
        start_date=datetime.datetime(2014, 1, 1, 6, 0, 0, tzinfo=utc),
        end_date=datetime.datetime(2016, 1, 1, 7, 0, 0, tzinfo=utc),
        product=product,
        price=20.0,
    )
    assert str(product_price.start_date).count("2014") == 1
    assert str(product_price.end_date).count("2016") == 1
    assert product_price.price == 20.0

    product_price_open_end = product_price_factory(
        start_date=datetime.datetime(2016, 1, 1, 6, 0, 0, tzinfo=utc),
        end_date=None,
        product=product,
        price=33.0,
    )
    assert str(product_price_open_end.start_date).count("2016") == 1
    assert product_price_open_end.end_date is None
    assert product_price_open_end.price is not None

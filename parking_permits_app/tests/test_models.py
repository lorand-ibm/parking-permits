import datetime

import pytest
from django.utils.timezone import utc


@pytest.mark.django_db
def test_zone_prices(parking_zone_factory, price_factory):
    zone = parking_zone_factory()
    zone_price = price_factory(
        start_date=datetime.datetime(2014, 1, 1, 6, 0, 0, tzinfo=utc),
        end_date=datetime.datetime(2016, 1, 1, 7, 0, 0, tzinfo=utc),
        zone=zone,
        price=20.0,
    )
    assert str(zone_price.start_date).count("2014") == 1
    assert str(zone_price.end_date).count("2016") == 1
    assert zone_price.price == 20.0

    zone_price_open_end = price_factory(
        start_date=datetime.datetime(2016, 1, 1, 6, 0, 0, tzinfo=utc),
        end_date=None,
        zone=zone,
        price=33.0,
    )
    assert str(zone_price_open_end.start_date).count("2016") == 1
    assert zone_price_open_end.end_date is None
    assert zone_price_open_end.price is not None

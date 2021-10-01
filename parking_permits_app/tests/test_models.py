import datetime

import pytest
from django.utils.timezone import utc

from parking_permits_app.tests.factories import ParkingZoneFactory, PriceFactory


@pytest.mark.django_db
def test_zone_prices():
    zone = ParkingZoneFactory()
    zone_price = PriceFactory(
        start_date=datetime.datetime(2014, 1, 1, 6, 0, 0, tzinfo=utc),
        end_date=datetime.datetime(2016, 1, 1, 7, 0, 0, tzinfo=utc),
        zone=zone,
        price=20.0,
    )
    assert str(zone_price.start_date).count("2014") == 1
    assert str(zone_price.end_date).count("2016") == 1
    assert zone_price.price == 20.0

    zone_price_open_end = PriceFactory(
        start_date=datetime.datetime(2016, 1, 1, 6, 0, 0, tzinfo=utc),
        end_date=None,
        zone=zone,
        price=33.0,
    )
    assert str(zone_price_open_end.start_date).count("2016") == 1
    assert zone_price_open_end.end_date is None
    assert zone_price_open_end.price is not None

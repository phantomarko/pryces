import pytest

from tests.fixtures.factories import open_stock_after_burn
from pryces.domain.stocks import Stock


@pytest.fixture
def sma50_crossing_stock() -> Stock:
    return open_stock_after_burn(
        current_price="150.00", previous_close_price="140.00", fifty_day_average="145.00"
    )


@pytest.fixture
def sma200_crossing_stock() -> Stock:
    return open_stock_after_burn(
        current_price="150.00", previous_close_price="130.00", two_hundred_day_average="140.00"
    )


@pytest.fixture
def close_to_sma50_from_below_stock() -> Stock:
    return open_stock_after_burn(
        current_price="100.00", previous_close_price="95.00", fifty_day_average="102.00"
    )


@pytest.fixture
def close_to_sma200_from_below_stock() -> Stock:
    return open_stock_after_burn(
        current_price="100.00", previous_close_price="95.00", two_hundred_day_average="102.00"
    )


@pytest.fixture
def close_to_sma50_from_above_stock() -> Stock:
    return open_stock_after_burn(
        current_price="100.00", previous_close_price="105.00", fifty_day_average="98.00"
    )


@pytest.fixture
def close_to_sma200_from_above_stock() -> Stock:
    return open_stock_after_burn(
        current_price="100.00", previous_close_price="105.00", two_hundred_day_average="98.00"
    )

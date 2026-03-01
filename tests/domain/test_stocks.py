from decimal import Decimal

from pryces.domain.notifications import NotificationType
from pryces.domain.stocks import GenerateNotificationsResult, MarketState, Stock, StockSnapshot


def test_stock_creation_with_required_fields():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

    assert stock.symbol == "AAPL"
    assert stock.current_price == Decimal("150.00")


def test_stock_creation_with_all_fields():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        name="Apple Inc.",
        currency="USD",
        previous_close_price=Decimal("149.50"),
        open_price=Decimal("149.75"),
        day_high=Decimal("151.00"),
        day_low=Decimal("149.00"),
        fifty_day_average=Decimal("145.00"),
        two_hundred_day_average=Decimal("140.00"),
        fifty_two_week_high=Decimal("160.00"),
        fifty_two_week_low=Decimal("120.00"),
    )

    assert stock.symbol == "AAPL"
    assert stock.current_price == Decimal("150.00")
    assert stock.name == "Apple Inc."
    assert stock.currency == "USD"
    assert stock.previous_close_price == Decimal("149.50")
    assert stock.open_price == Decimal("149.75")
    assert stock.day_high == Decimal("151.00")
    assert stock.day_low == Decimal("149.00")
    assert stock.fifty_day_average == Decimal("145.00")
    assert stock.two_hundred_day_average == Decimal("140.00")
    assert stock.fifty_two_week_high == Decimal("160.00")
    assert stock.fifty_two_week_low == Decimal("120.00")


def test_stock_is_immutable():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

    try:
        stock.symbol = "GOOGL"
        assert False, "Should not be able to modify frozen dataclass"
    except AttributeError:
        pass


def test_has_crossed_fifty_day_average_returns_false_when_fields_are_missing():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    assert stock._has_crossed_fifty_day_average() is False

    stock_with_previous = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("140.00"),
    )
    assert stock_with_previous._has_crossed_fifty_day_average() is False

    stock_with_average = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        fifty_day_average=Decimal("145.00"),
    )
    assert stock_with_average._has_crossed_fifty_day_average() is False


def test_has_crossed_fifty_day_average_detects_crossing_above():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("140.00"),
        fifty_day_average=Decimal("145.00"),
    )
    assert stock._has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_detects_crossing_below():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("140.00"),
        previous_close_price=Decimal("150.00"),
        fifty_day_average=Decimal("145.00"),
    )
    assert stock._has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_returns_false_when_no_crossing():
    stock_both_above = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("148.00"),
        fifty_day_average=Decimal("145.00"),
    )
    assert stock_both_above._has_crossed_fifty_day_average() is False

    stock_both_below = Stock(
        symbol="AAPL",
        current_price=Decimal("140.00"),
        previous_close_price=Decimal("142.00"),
        fifty_day_average=Decimal("145.00"),
    )
    assert stock_both_below._has_crossed_fifty_day_average() is False


def test_has_crossed_fifty_day_average_detects_crossing_above_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("145.00"),
        previous_close_price=Decimal("140.00"),
        fifty_day_average=Decimal("145.00"),
    )
    assert stock._has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_detects_crossing_below_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("145.00"),
        previous_close_price=Decimal("150.00"),
        fifty_day_average=Decimal("145.00"),
    )
    assert stock._has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_returns_false_when_previous_equals_average():
    stock_current_above = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("145.00"),
        fifty_day_average=Decimal("145.00"),
    )
    assert stock_current_above._has_crossed_fifty_day_average() is False

    stock_current_below = Stock(
        symbol="AAPL",
        current_price=Decimal("140.00"),
        previous_close_price=Decimal("145.00"),
        fifty_day_average=Decimal("145.00"),
    )
    assert stock_current_below._has_crossed_fifty_day_average() is False


def test_is_close_to_fifty_day_average_returns_false_when_fields_are_missing():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    assert stock._is_close_to_fifty_day_average() is False

    stock_with_previous = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("140.00"),
    )
    assert stock_with_previous._is_close_to_fifty_day_average() is False

    stock_with_average = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        fifty_day_average=Decimal("145.00"),
    )
    assert stock_with_average._is_close_to_fifty_day_average() is False


def test_is_close_to_fifty_day_average_returns_true_when_approaching_from_below_within_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("95.00"),
        fifty_day_average=Decimal("105.00"),
    )
    assert stock._is_close_to_fifty_day_average() is True


def test_is_close_to_fifty_day_average_returns_true_when_approaching_from_above_within_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("105.00"),
        fifty_day_average=Decimal("95.00"),
    )
    assert stock._is_close_to_fifty_day_average() is True


def test_is_close_to_fifty_day_average_returns_false_when_approaching_from_below_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("95.00"),
        fifty_day_average=Decimal("106.00"),
    )
    assert stock._is_close_to_fifty_day_average() is False


def test_is_close_to_fifty_day_average_returns_false_when_approaching_from_above_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("105.00"),
        fifty_day_average=Decimal("94.00"),
    )
    assert stock._is_close_to_fifty_day_average() is False


def test_is_close_to_fifty_day_average_returns_true_at_exact_threshold_from_below():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("95.00"),
        fifty_day_average=Decimal("105.00"),
    )
    assert stock._is_close_to_fifty_day_average() is True


def test_is_close_to_fifty_day_average_returns_true_at_exact_threshold_from_above():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("105.00"),
        fifty_day_average=Decimal("95.00"),
    )
    assert stock._is_close_to_fifty_day_average() is True


def test_is_close_to_fifty_day_average_returns_false_when_previous_close_on_same_side_as_price():
    stock_both_above = Stock(
        symbol="AAPL",
        current_price=Decimal("110.00"),
        previous_close_price=Decimal("108.00"),
        fifty_day_average=Decimal("100.00"),
    )
    assert stock_both_above._is_close_to_fifty_day_average() is False

    stock_both_below = Stock(
        symbol="AAPL",
        current_price=Decimal("90.00"),
        previous_close_price=Decimal("92.00"),
        fifty_day_average=Decimal("100.00"),
    )
    assert stock_both_below._is_close_to_fifty_day_average() is False


def test_is_close_to_fifty_day_average_returns_false_when_previous_equals_average():
    stock_current_above = Stock(
        symbol="AAPL",
        current_price=Decimal("103.00"),
        previous_close_price=Decimal("100.00"),
        fifty_day_average=Decimal("100.00"),
    )
    assert stock_current_above._is_close_to_fifty_day_average() is False

    stock_current_below = Stock(
        symbol="AAPL",
        current_price=Decimal("97.00"),
        previous_close_price=Decimal("100.00"),
        fifty_day_average=Decimal("100.00"),
    )
    assert stock_current_below._is_close_to_fifty_day_average() is False


def test_generate_notifications_adds_close_to_sma50_when_approaching_from_below():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("95.00"),
        fifty_day_average=Decimal("103.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA50 in types


def test_generate_notifications_adds_close_to_sma50_when_approaching_from_above():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("105.00"),
        fifty_day_average=Decimal("97.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA50 in types


def test_generate_notifications_does_not_add_close_to_sma50_when_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("95.00"),
        fifty_day_average=Decimal("110.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA50 not in types


def test_generate_notifications_does_not_add_close_to_sma50_when_previous_close_on_same_side():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("110.00"),
        previous_close_price=Decimal("108.00"),
        fifty_day_average=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA50 not in types


def test_is_close_to_two_hundred_day_average_returns_false_when_fields_are_missing():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    assert stock._is_close_to_two_hundred_day_average() is False

    stock_with_previous = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("140.00"),
    )
    assert stock_with_previous._is_close_to_two_hundred_day_average() is False

    stock_with_average = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        two_hundred_day_average=Decimal("145.00"),
    )
    assert stock_with_average._is_close_to_two_hundred_day_average() is False


def test_is_close_to_two_hundred_day_average_returns_true_when_approaching_from_below_within_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("95.00"),
        two_hundred_day_average=Decimal("105.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is True


def test_is_close_to_two_hundred_day_average_returns_true_when_approaching_from_above_within_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("105.00"),
        two_hundred_day_average=Decimal("95.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is True


def test_is_close_to_two_hundred_day_average_returns_false_when_approaching_from_below_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("95.00"),
        two_hundred_day_average=Decimal("106.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is False


def test_is_close_to_two_hundred_day_average_returns_false_when_approaching_from_above_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("105.00"),
        two_hundred_day_average=Decimal("94.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is False


def test_is_close_to_two_hundred_day_average_returns_true_at_exact_threshold_from_below():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("95.00"),
        two_hundred_day_average=Decimal("105.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is True


def test_is_close_to_two_hundred_day_average_returns_true_at_exact_threshold_from_above():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("105.00"),
        two_hundred_day_average=Decimal("95.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is True


def test_is_close_to_two_hundred_day_average_returns_false_when_previous_close_on_same_side_as_price():
    stock_both_above = Stock(
        symbol="AAPL",
        current_price=Decimal("110.00"),
        previous_close_price=Decimal("108.00"),
        two_hundred_day_average=Decimal("100.00"),
    )
    assert stock_both_above._is_close_to_two_hundred_day_average() is False

    stock_both_below = Stock(
        symbol="AAPL",
        current_price=Decimal("90.00"),
        previous_close_price=Decimal("92.00"),
        two_hundred_day_average=Decimal("100.00"),
    )
    assert stock_both_below._is_close_to_two_hundred_day_average() is False


def test_is_close_to_two_hundred_day_average_returns_false_when_previous_equals_average():
    stock_current_above = Stock(
        symbol="AAPL",
        current_price=Decimal("103.00"),
        previous_close_price=Decimal("100.00"),
        two_hundred_day_average=Decimal("100.00"),
    )
    assert stock_current_above._is_close_to_two_hundred_day_average() is False

    stock_current_below = Stock(
        symbol="AAPL",
        current_price=Decimal("97.00"),
        previous_close_price=Decimal("100.00"),
        two_hundred_day_average=Decimal("100.00"),
    )
    assert stock_current_below._is_close_to_two_hundred_day_average() is False


def test_generate_notifications_adds_close_to_sma200_when_approaching_from_below():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("95.00"),
        two_hundred_day_average=Decimal("103.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA200 in types


def test_generate_notifications_adds_close_to_sma200_when_approaching_from_above():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("105.00"),
        two_hundred_day_average=Decimal("97.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA200 in types


def test_generate_notifications_does_not_add_close_to_sma200_when_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("95.00"),
        two_hundred_day_average=Decimal("110.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA200 not in types


def test_generate_notifications_does_not_add_close_to_sma200_when_previous_close_on_same_side():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("110.00"),
        previous_close_price=Decimal("108.00"),
        two_hundred_day_average=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA200 not in types


def test_has_crossed_two_hundred_day_average_returns_false_when_fields_are_missing():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    assert stock._has_crossed_two_hundred_day_average() is False

    stock_with_previous = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("130.00"),
    )
    assert stock_with_previous._has_crossed_two_hundred_day_average() is False

    stock_with_average = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        two_hundred_day_average=Decimal("140.00"),
    )
    assert stock_with_average._has_crossed_two_hundred_day_average() is False


def test_has_crossed_two_hundred_day_average_detects_crossing_above():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("130.00"),
        two_hundred_day_average=Decimal("140.00"),
    )
    assert stock._has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_detects_crossing_below():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("130.00"),
        previous_close_price=Decimal("150.00"),
        two_hundred_day_average=Decimal("140.00"),
    )
    assert stock._has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_returns_false_when_no_crossing():
    stock_both_above = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("148.00"),
        two_hundred_day_average=Decimal("140.00"),
    )
    assert stock_both_above._has_crossed_two_hundred_day_average() is False

    stock_both_below = Stock(
        symbol="AAPL",
        current_price=Decimal("130.00"),
        previous_close_price=Decimal("135.00"),
        two_hundred_day_average=Decimal("140.00"),
    )
    assert stock_both_below._has_crossed_two_hundred_day_average() is False


def test_has_crossed_two_hundred_day_average_detects_crossing_above_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("140.00"),
        previous_close_price=Decimal("130.00"),
        two_hundred_day_average=Decimal("140.00"),
    )
    assert stock._has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_detects_crossing_below_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("140.00"),
        previous_close_price=Decimal("150.00"),
        two_hundred_day_average=Decimal("140.00"),
    )
    assert stock._has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_returns_false_when_previous_equals_average():
    stock_current_above = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("140.00"),
        two_hundred_day_average=Decimal("140.00"),
    )
    assert stock_current_above._has_crossed_two_hundred_day_average() is False

    stock_current_below = Stock(
        symbol="AAPL",
        current_price=Decimal("130.00"),
        previous_close_price=Decimal("140.00"),
        two_hundred_day_average=Decimal("140.00"),
    )
    assert stock_current_below._has_crossed_two_hundred_day_average() is False


def test_change_percentage_from_previous_close_returns_none_when_previous_close_is_none():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

    assert stock._change_percentage_from_previous_close() is None


def test_change_percentage_from_previous_close_returns_positive_percentage():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("100.00"),
    )

    assert stock._change_percentage_from_previous_close() == Decimal("50.00")


def test_change_percentage_from_previous_close_returns_negative_percentage():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("90.00"),
        previous_close_price=Decimal("100.00"),
    )

    assert stock._change_percentage_from_previous_close() == Decimal("-10.00")


def test_change_percentage_from_previous_close_returns_zero_when_prices_are_equal():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("100.00"),
    )

    assert stock._change_percentage_from_previous_close() == Decimal("0.00")


def test_stock_optional_fields_default_to_none():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

    assert stock.name is None
    assert stock.currency is None
    assert stock.previous_close_price is None
    assert stock.open_price is None
    assert stock.day_high is None
    assert stock.day_low is None
    assert stock.fifty_day_average is None
    assert stock.two_hundred_day_average is None
    assert stock.fifty_two_week_high is None
    assert stock.fifty_two_week_low is None


def test_stock_notifications_defaults_to_empty_list():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

    assert stock.notifications == []


def test_generate_notifications_adds_fifty_day_notification():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("140.00"),
        fifty_day_average=Decimal("145.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 3
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.SMA50_CROSSED,
        NotificationType.FIVE_PERCENT_INCREASE,
    }


def test_generate_notifications_adds_two_hundred_day_notification():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("130.00"),
        two_hundred_day_average=Decimal("140.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 3
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.SMA200_CROSSED,
        NotificationType.FIFTEEN_PERCENT_INCREASE,
    }


def test_generate_notifications_adds_both_notifications():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("130.00"),
        fifty_day_average=Decimal("145.00"),
        two_hundred_day_average=Decimal("140.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 4
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.SMA50_CROSSED,
        NotificationType.SMA200_CROSSED,
        NotificationType.FIFTEEN_PERCENT_INCREASE,
    }


def test_generate_notifications_adds_no_notifications_when_no_crossing():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("148.00"),
        fifty_day_average=Decimal("120.00"),
        two_hundred_day_average=Decimal("110.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN
    sma_types = {NotificationType.SMA50_CROSSED, NotificationType.SMA200_CROSSED}
    assert not any(n.type in sma_types for n in stock.notifications)


def test_is_market_state_open_returns_true_when_market_state_is_open():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        market_state=MarketState.OPEN,
    )

    assert stock._is_market_state_open() is True


def test_is_market_state_open_returns_false_when_market_state_is_closed():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        market_state=MarketState.CLOSED,
    )

    assert stock._is_market_state_open() is False


def test_is_market_state_open_returns_false_when_market_state_is_none():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

    assert stock._is_market_state_open() is False


def test_generate_notifications_adds_regular_market_open_notification():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        open_price=Decimal("149.75"),
        previous_close_price=Decimal("148.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN


def test_generate_notifications_adds_regular_market_open_with_current_price_fallback():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("148.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN


def test_generate_notifications_does_not_add_regular_market_open_when_market_closed():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        open_price=Decimal("149.75"),
        previous_close_price=Decimal("148.00"),
        market_state=MarketState.CLOSED,
    )

    stock.generate_notifications()

    assert stock.notifications == []


def test_is_market_state_post_returns_true_when_market_state_is_post():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        market_state=MarketState.POST,
    )

    assert stock._is_market_state_post() is True


def test_is_market_state_post_returns_false_for_other_states():
    for state in [MarketState.OPEN, MarketState.PRE, MarketState.CLOSED]:
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=state,
        )
        assert stock._is_market_state_post() is False


def test_is_market_state_post_returns_false_when_market_state_is_none():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

    assert stock._is_market_state_post() is False


def test_generate_notifications_adds_regular_market_closed_when_post():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        market_state=MarketState.POST,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_CLOSED


def test_generate_notifications_adds_twenty_percent_increase():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("121.00"),
        previous_close_price=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.TWENTY_PERCENT_INCREASE,
    }


def test_generate_notifications_adds_fifteen_percent_increase():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("116.00"),
        previous_close_price=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.FIFTEEN_PERCENT_INCREASE,
    }


def test_generate_notifications_adds_ten_percent_increase():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("111.00"),
        previous_close_price=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.TEN_PERCENT_INCREASE,
    }


def test_generate_notifications_adds_five_percent_increase():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("106.00"),
        previous_close_price=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.FIVE_PERCENT_INCREASE,
    }


def test_generate_notifications_adds_twenty_percent_decrease():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("79.00"),
        previous_close_price=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.TWENTY_PERCENT_DECREASE,
    }


def test_generate_notifications_adds_fifteen_percent_decrease():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("84.00"),
        previous_close_price=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.FIFTEEN_PERCENT_DECREASE,
    }


def test_generate_notifications_adds_ten_percent_decrease():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("89.00"),
        previous_close_price=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.TEN_PERCENT_DECREASE,
    }


def test_generate_notifications_adds_five_percent_decrease():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("94.00"),
        previous_close_price=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.FIVE_PERCENT_DECREASE,
    }


def test_generate_notifications_no_percentage_below_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("104.00"),
        previous_close_price=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN


def test_generate_notifications_percentage_at_exact_threshold():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("105.00"),
        previous_close_price=Decimal("100.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.FIVE_PERCENT_INCREASE,
    }


def test_generate_new_52_week_high_notification_does_not_add_when_no_snapshot():
    stock = Stock(symbol="AAPL", current_price=Decimal("200.00"), market_state=MarketState.OPEN)

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.NEW_52_WEEK_HIGH not in types


def test_generate_new_52_week_high_notification_does_not_add_when_snapshot_has_no_52_week_high():
    stock = Stock(symbol="AAPL", current_price=Decimal("180.00"), market_state=MarketState.OPEN)
    source = Stock(symbol="AAPL", current_price=Decimal("200.00"), market_state=MarketState.OPEN)
    stock.update(source)

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.NEW_52_WEEK_HIGH not in types


def test_generate_new_52_week_high_notification_does_not_add_when_current_price_equals_snapshot_52_week_high():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("170.00"),
        fifty_two_week_high=Decimal("180.00"),
        market_state=MarketState.OPEN,
    )
    source = Stock(symbol="AAPL", current_price=Decimal("180.00"), market_state=MarketState.OPEN)
    stock.update(source)

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.NEW_52_WEEK_HIGH not in types


def test_generate_new_52_week_high_notification_does_not_add_when_current_price_below_snapshot_52_week_high():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("160.00"),
        fifty_two_week_high=Decimal("180.00"),
        market_state=MarketState.OPEN,
    )
    source = Stock(symbol="AAPL", current_price=Decimal("170.00"), market_state=MarketState.OPEN)
    stock.update(source)

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.NEW_52_WEEK_HIGH not in types


def test_generate_new_52_week_high_notification_adds_when_current_price_exceeds_snapshot_52_week_high():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("170.00"),
        fifty_two_week_high=Decimal("180.00"),
        market_state=MarketState.OPEN,
    )
    source = Stock(symbol="AAPL", current_price=Decimal("200.00"), market_state=MarketState.OPEN)
    stock.update(source)

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.NEW_52_WEEK_HIGH in types


def test_generate_new_52_week_low_notification_does_not_add_when_no_snapshot():
    stock = Stock(symbol="AAPL", current_price=Decimal("100.00"), market_state=MarketState.OPEN)

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.NEW_52_WEEK_LOW not in types


def test_generate_new_52_week_low_notification_does_not_add_when_snapshot_has_no_52_week_low():
    stock = Stock(symbol="AAPL", current_price=Decimal("120.00"), market_state=MarketState.OPEN)
    source = Stock(symbol="AAPL", current_price=Decimal("100.00"), market_state=MarketState.OPEN)
    stock.update(source)

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.NEW_52_WEEK_LOW not in types


def test_generate_new_52_week_low_notification_does_not_add_when_current_price_equals_snapshot_52_week_low():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("130.00"),
        fifty_two_week_low=Decimal("120.00"),
        market_state=MarketState.OPEN,
    )
    source = Stock(symbol="AAPL", current_price=Decimal("120.00"), market_state=MarketState.OPEN)
    stock.update(source)

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.NEW_52_WEEK_LOW not in types


def test_generate_new_52_week_low_notification_does_not_add_when_current_price_above_snapshot_52_week_low():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("140.00"),
        fifty_two_week_low=Decimal("120.00"),
        market_state=MarketState.OPEN,
    )
    source = Stock(symbol="AAPL", current_price=Decimal("130.00"), market_state=MarketState.OPEN)
    stock.update(source)

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.NEW_52_WEEK_LOW not in types


def test_generate_new_52_week_low_notification_adds_when_current_price_falls_below_snapshot_52_week_low():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("130.00"),
        fifty_two_week_low=Decimal("120.00"),
        market_state=MarketState.OPEN,
    )
    source = Stock(symbol="AAPL", current_price=Decimal("100.00"), market_state=MarketState.OPEN)
    stock.update(source)

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.NEW_52_WEEK_LOW in types


def test_generate_notifications_no_percentage_when_previous_close_none():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        market_state=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN


def test_stock_price_delay_in_minutes_accepts_int_and_none():
    stock_real_time = Stock(
        symbol="AAPL", current_price=Decimal("150.00"), price_delay_in_minutes=0
    )
    assert stock_real_time.price_delay_in_minutes == 0

    stock_delayed = Stock(symbol="AAPL", current_price=Decimal("150.00"), price_delay_in_minutes=15)
    assert stock_delayed.price_delay_in_minutes == 15

    stock_none = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    assert stock_none.price_delay_in_minutes is None


def test_snapshot_defaults_to_none():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

    assert stock.snapshot is None


def test_update_captures_snapshot_of_previous_state():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        fifty_two_week_high=Decimal("160.00"),
        market_state=MarketState.OPEN,
        price_delay_in_minutes=0,
    )
    source = Stock(
        symbol="AAPL",
        current_price=Decimal("155.00"),
        fifty_two_week_high=Decimal("165.00"),
        market_state=MarketState.OPEN,
    )

    stock.update(source)

    assert stock.snapshot is not None
    assert stock.snapshot.current_price == Decimal("150.00")
    assert stock.snapshot.fifty_two_week_high == Decimal("160.00")
    assert stock.snapshot.market_state == MarketState.OPEN
    assert stock.snapshot.price_delay_in_minutes == 0


def test_update_copies_fields_from_source():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    source = Stock(
        symbol="AAPL",
        current_price=Decimal("155.00"),
        name="Apple Inc.",
        currency="USD",
        previous_close_price=Decimal("149.00"),
        open_price=Decimal("150.00"),
        day_high=Decimal("156.00"),
        day_low=Decimal("148.00"),
        fifty_day_average=Decimal("145.00"),
        two_hundred_day_average=Decimal("140.00"),
        fifty_two_week_high=Decimal("170.00"),
        fifty_two_week_low=Decimal("120.00"),
        market_state=MarketState.OPEN,
        price_delay_in_minutes=15,
    )

    stock.update(source)

    assert stock.current_price == Decimal("155.00")
    assert stock.name == "Apple Inc."
    assert stock.currency == "USD"
    assert stock.previous_close_price == Decimal("149.00")
    assert stock.open_price == Decimal("150.00")
    assert stock.day_high == Decimal("156.00")
    assert stock.day_low == Decimal("148.00")
    assert stock.fifty_day_average == Decimal("145.00")
    assert stock.two_hundred_day_average == Decimal("140.00")
    assert stock.fifty_two_week_high == Decimal("170.00")
    assert stock.fifty_two_week_low == Decimal("120.00")
    assert stock.market_state == MarketState.OPEN
    assert stock.price_delay_in_minutes == 15


def test_update_preserves_symbol():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    source = Stock(symbol="AAPL", current_price=Decimal("155.00"))

    stock.update(source)

    assert stock.symbol == "AAPL"


def test_update_preserves_notifications():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("148.00"),
        market_state=MarketState.OPEN,
    )
    stock.generate_notifications()
    count_before = len(stock.notifications)
    assert count_before > 0

    source = Stock(symbol="AAPL", current_price=Decimal("155.00"))
    stock.update(source)

    assert len(stock.notifications) == count_before


def test_stock_snapshot_is_frozen():
    snapshot = StockSnapshot(
        current_price=Decimal("150.00"),
        previous_close_price=None,
        open_price=None,
        day_high=None,
        day_low=None,
        fifty_day_average=None,
        two_hundred_day_average=None,
        fifty_two_week_high=None,
        fifty_two_week_low=None,
        market_state=None,
        price_delay_in_minutes=None,
    )

    try:
        snapshot.current_price = Decimal("200.00")
        assert False, "Should not be able to modify frozen dataclass"
    except AttributeError:
        pass


def test_is_market_state_transition_returns_false_when_no_snapshot():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)

    assert stock.is_market_state_transition() is False


def test_is_market_state_transition_returns_true_when_pre_to_open():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.PRE)
    source = Stock(symbol="AAPL", current_price=Decimal("155.00"), market_state=MarketState.OPEN)
    stock.update(source)

    assert stock.is_market_state_transition() is True


def test_is_market_state_transition_returns_true_when_open_to_post():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
    source = Stock(symbol="AAPL", current_price=Decimal("155.00"), market_state=MarketState.POST)
    stock.update(source)

    assert stock.is_market_state_transition() is True


def test_is_market_state_transition_returns_false_when_same_state():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
    source = Stock(symbol="AAPL", current_price=Decimal("155.00"), market_state=MarketState.OPEN)
    stock.update(source)

    assert stock.is_market_state_transition() is False


def test_is_market_state_transition_returns_false_when_transition_to_non_open_post():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
    source = Stock(symbol="AAPL", current_price=Decimal("155.00"), market_state=MarketState.PRE)
    stock.update(source)

    assert stock.is_market_state_transition() is False


def test_generate_notifications_deduplicates_by_type():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("148.00"),
        market_state=MarketState.OPEN,
    )
    result1 = stock.generate_notifications()
    first_count = len(stock.notifications)
    assert first_count > 0
    assert len(result1.new_notifications) == first_count

    result2 = stock.generate_notifications()

    assert len(stock.notifications) == first_count
    assert result2.new_notifications == []


def test_generate_notifications_appends_target_price_reached_when_target_is_reached():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.OPEN,
    )
    stock.sync_targets([Decimal("200.00")])
    source = Stock(
        symbol="AAPL",
        current_price=Decimal("200.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.OPEN,
    )
    stock.update(source)

    stock.generate_notifications()

    types = [n.type for n in stock.notifications]
    assert NotificationType.TARGET_PRICE_REACHED in types


def test_generate_notifications_removes_triggered_targets_from_stock():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.OPEN,
    )
    stock.sync_targets([Decimal("200.00")])
    source = Stock(
        symbol="AAPL",
        current_price=Decimal("200.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.OPEN,
    )
    stock.update(source)

    result = stock.generate_notifications()

    assert isinstance(result, GenerateNotificationsResult)
    assert len(result.new_notifications) > 0
    assert stock.targets == []


def test_generate_notifications_does_not_include_unreached_target():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("148.00"),
        market_state=MarketState.OPEN,
    )
    stock.sync_targets([Decimal("200.00")])
    source = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("148.00"),
        market_state=MarketState.OPEN,
    )
    stock.update(source)

    stock.generate_notifications()

    assert len(stock.targets) == 1
    types = [n.type for n in stock.notifications]
    assert NotificationType.TARGET_PRICE_REACHED not in types


def test_generate_notifications_target_notification_message_contains_symbol_and_target():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.OPEN,
    )
    stock.sync_targets([Decimal("200.00")])
    source = Stock(
        symbol="AAPL",
        current_price=Decimal("200.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.OPEN,
    )
    stock.update(source)

    stock.generate_notifications()

    target_notifications = [
        n for n in stock.notifications if n.type == NotificationType.TARGET_PRICE_REACHED
    ]
    assert len(target_notifications) == 1
    assert "AAPL" in target_notifications[0].message
    assert "200.00" in target_notifications[0].message


def test_generate_notifications_ignores_targets_when_market_is_post():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.POST,
    )
    stock.sync_targets([Decimal("200.00")])
    source = Stock(
        symbol="AAPL",
        current_price=Decimal("200.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.POST,
    )
    stock.update(source)

    stock.generate_notifications()

    assert len(stock.targets) == 1
    types = [n.type for n in stock.notifications]
    assert NotificationType.TARGET_PRICE_REACHED not in types


def test_generate_notifications_removes_multiple_triggered_targets():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("295.00"),
        market_state=MarketState.OPEN,
    )
    stock.sync_targets([Decimal("200.00"), Decimal("250.00")])
    source = Stock(
        symbol="AAPL",
        current_price=Decimal("300.00"),
        previous_close_price=Decimal("295.00"),
        market_state=MarketState.OPEN,
    )
    stock.update(source)

    stock.generate_notifications()

    assert stock.targets == []
    target_notifications = [
        n for n in stock.notifications if n.type == NotificationType.TARGET_PRICE_REACHED
    ]
    assert len(target_notifications) == 2


def test_generate_notifications_target_price_reached_is_never_deduplicated():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("100.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.OPEN,
    )
    stock.sync_targets([Decimal("200.00")])
    source1 = Stock(
        symbol="AAPL",
        current_price=Decimal("200.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.OPEN,
    )
    stock.update(source1)
    stock.generate_notifications()

    stock.sync_targets([Decimal("250.00")])
    source2 = Stock(
        symbol="AAPL",
        current_price=Decimal("250.00"),
        previous_close_price=Decimal("195.00"),
        market_state=MarketState.OPEN,
    )
    stock.update(source2)
    stock.generate_notifications()

    target_notifications = [
        n for n in stock.notifications if n.type == NotificationType.TARGET_PRICE_REACHED
    ]
    assert len(target_notifications) == 2


def test_generate_notifications_returns_new_notifications_only():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("101.00"),
        previous_close_price=Decimal("99.00"),
        fifty_day_average=Decimal("100.00"),
        two_hundred_day_average=Decimal("80.00"),
        market_state=MarketState.OPEN,
    )
    result1 = stock.generate_notifications()
    assert len(result1.new_notifications) > 0

    result2 = stock.generate_notifications()

    assert result2.new_notifications == []


def test_sync_targets_sets_entry_price():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

    stock.sync_targets([Decimal("200.00")])

    assert len(stock.targets) == 1
    assert stock.targets[0].entry == Decimal("150.00")


def test_sync_targets_preserves_existing_target():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    stock.sync_targets([Decimal("200.00")])
    original_target = stock.targets[0]

    stock.sync_targets([Decimal("200.00")])

    assert len(stock.targets) == 1
    assert stock.targets[0].entry == Decimal("150.00")
    assert stock.targets[0] is original_target


def test_sync_targets_removes_missing_targets():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    stock.sync_targets([Decimal("200.00"), Decimal("250.00")])

    stock.sync_targets([Decimal("200.00")])

    assert len(stock.targets) == 1
    assert stock.targets[0].target == Decimal("200.00")


def test_sync_targets_clears_all_on_empty_list():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    stock.sync_targets([Decimal("200.00")])

    stock.sync_targets([])

    assert stock.targets == []


def test_sync_targets_adds_new_and_preserves_existing():
    stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
    stock.sync_targets([Decimal("200.00")])
    original_target = stock.targets[0]

    stock.sync_targets([Decimal("200.00"), Decimal("250.00")])

    assert len(stock.targets) == 2
    assert stock.targets[0] is original_target
    assert stock.targets[1].target == Decimal("250.00")
    assert stock.targets[1].entry == Decimal("150.00")


def test_drain_fulfilled_targets_returns_fulfilled_targets():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("145.00"),
        market_state=MarketState.OPEN,
    )
    stock.sync_targets([Decimal("150.00")])
    stock.generate_notifications()

    fulfilled = stock.drain_fulfilled_targets()

    assert len(fulfilled) == 1
    assert fulfilled[0] == Decimal("150.00")


def test_drain_fulfilled_targets_clears_list_after_drain():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("145.00"),
        market_state=MarketState.OPEN,
    )
    stock.sync_targets([Decimal("150.00")])
    stock.generate_notifications()
    stock.drain_fulfilled_targets()

    second_drain = stock.drain_fulfilled_targets()

    assert second_drain == []


def test_drain_fulfilled_targets_returns_empty_when_no_targets_fulfilled():
    stock = Stock(
        symbol="AAPL",
        current_price=Decimal("150.00"),
        previous_close_price=Decimal("145.00"),
        market_state=MarketState.OPEN,
    )
    stock.sync_targets([Decimal("200.00")])
    stock.generate_notifications()

    fulfilled = stock.drain_fulfilled_targets()

    assert fulfilled == []

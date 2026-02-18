from decimal import Decimal

from pryces.domain.notifications import NotificationType
from pryces.domain.stocks import MarketState, Stock


def test_stock_creation_with_required_fields():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))

    assert stock.symbol == "AAPL"
    assert stock.currentPrice == Decimal("150.00")


def test_stock_creation_with_all_fields():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        name="Apple Inc.",
        currency="USD",
        previousClosePrice=Decimal("149.50"),
        openPrice=Decimal("149.75"),
        dayHigh=Decimal("151.00"),
        dayLow=Decimal("149.00"),
        fiftyDayAverage=Decimal("145.00"),
        twoHundredDayAverage=Decimal("140.00"),
        fiftyTwoWeekHigh=Decimal("160.00"),
        fiftyTwoWeekLow=Decimal("120.00"),
    )

    assert stock.symbol == "AAPL"
    assert stock.currentPrice == Decimal("150.00")
    assert stock.name == "Apple Inc."
    assert stock.currency == "USD"
    assert stock.previousClosePrice == Decimal("149.50")
    assert stock.openPrice == Decimal("149.75")
    assert stock.dayHigh == Decimal("151.00")
    assert stock.dayLow == Decimal("149.00")
    assert stock.fiftyDayAverage == Decimal("145.00")
    assert stock.twoHundredDayAverage == Decimal("140.00")
    assert stock.fiftyTwoWeekHigh == Decimal("160.00")
    assert stock.fiftyTwoWeekLow == Decimal("120.00")


def test_stock_is_immutable():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))

    try:
        stock.symbol = "GOOGL"
        assert False, "Should not be able to modify frozen dataclass"
    except AttributeError:
        pass


def test_has_crossed_fifty_day_average_returns_false_when_fields_are_missing():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))
    assert stock._has_crossed_fifty_day_average() is False

    stock_with_previous = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("140.00"),
    )
    assert stock_with_previous._has_crossed_fifty_day_average() is False

    stock_with_average = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_with_average._has_crossed_fifty_day_average() is False


def test_has_crossed_fifty_day_average_detects_crossing_above():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("140.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock._has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_detects_crossing_below():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("140.00"),
        previousClosePrice=Decimal("150.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock._has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_returns_false_when_no_crossing():
    stock_both_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("148.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_both_above._has_crossed_fifty_day_average() is False

    stock_both_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("140.00"),
        previousClosePrice=Decimal("142.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_both_below._has_crossed_fifty_day_average() is False


def test_has_crossed_fifty_day_average_detects_crossing_above_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("145.00"),
        previousClosePrice=Decimal("140.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock._has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_detects_crossing_below_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("145.00"),
        previousClosePrice=Decimal("150.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock._has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_returns_false_when_previous_equals_average():
    stock_current_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("145.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_current_above._has_crossed_fifty_day_average() is False

    stock_current_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("140.00"),
        previousClosePrice=Decimal("145.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_current_below._has_crossed_fifty_day_average() is False


def test_is_close_to_fifty_day_average_returns_false_when_fields_are_missing():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))
    assert stock._is_close_to_fifty_day_average() is False

    stock_with_previous = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("140.00"),
    )
    assert stock_with_previous._is_close_to_fifty_day_average() is False

    stock_with_average = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_with_average._is_close_to_fifty_day_average() is False


def test_is_close_to_fifty_day_average_returns_true_when_approaching_from_below_within_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("95.00"),
        fiftyDayAverage=Decimal("105.00"),
    )
    assert stock._is_close_to_fifty_day_average() is True


def test_is_close_to_fifty_day_average_returns_true_when_approaching_from_above_within_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("105.00"),
        fiftyDayAverage=Decimal("95.00"),
    )
    assert stock._is_close_to_fifty_day_average() is True


def test_is_close_to_fifty_day_average_returns_false_when_approaching_from_below_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("95.00"),
        fiftyDayAverage=Decimal("106.00"),
    )
    assert stock._is_close_to_fifty_day_average() is False


def test_is_close_to_fifty_day_average_returns_false_when_approaching_from_above_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("105.00"),
        fiftyDayAverage=Decimal("94.00"),
    )
    assert stock._is_close_to_fifty_day_average() is False


def test_is_close_to_fifty_day_average_returns_true_at_exact_threshold_from_below():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("95.00"),
        fiftyDayAverage=Decimal("105.00"),
    )
    assert stock._is_close_to_fifty_day_average() is True


def test_is_close_to_fifty_day_average_returns_true_at_exact_threshold_from_above():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("105.00"),
        fiftyDayAverage=Decimal("95.00"),
    )
    assert stock._is_close_to_fifty_day_average() is True


def test_is_close_to_fifty_day_average_returns_false_when_previous_close_on_same_side_as_price():
    stock_both_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("110.00"),
        previousClosePrice=Decimal("108.00"),
        fiftyDayAverage=Decimal("100.00"),
    )
    assert stock_both_above._is_close_to_fifty_day_average() is False

    stock_both_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("90.00"),
        previousClosePrice=Decimal("92.00"),
        fiftyDayAverage=Decimal("100.00"),
    )
    assert stock_both_below._is_close_to_fifty_day_average() is False


def test_is_close_to_fifty_day_average_returns_false_when_previous_equals_average():
    stock_current_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("103.00"),
        previousClosePrice=Decimal("100.00"),
        fiftyDayAverage=Decimal("100.00"),
    )
    assert stock_current_above._is_close_to_fifty_day_average() is False

    stock_current_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("97.00"),
        previousClosePrice=Decimal("100.00"),
        fiftyDayAverage=Decimal("100.00"),
    )
    assert stock_current_below._is_close_to_fifty_day_average() is False


def test_generate_notifications_adds_close_to_sma50_when_approaching_from_below():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("95.00"),
        fiftyDayAverage=Decimal("103.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA50 in types


def test_generate_notifications_adds_close_to_sma50_when_approaching_from_above():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("105.00"),
        fiftyDayAverage=Decimal("97.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA50 in types


def test_generate_notifications_does_not_add_close_to_sma50_when_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("95.00"),
        fiftyDayAverage=Decimal("110.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA50 not in types


def test_generate_notifications_does_not_add_close_to_sma50_when_previous_close_on_same_side():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("110.00"),
        previousClosePrice=Decimal("108.00"),
        fiftyDayAverage=Decimal("100.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA50 not in types


def test_is_close_to_two_hundred_day_average_returns_false_when_fields_are_missing():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))
    assert stock._is_close_to_two_hundred_day_average() is False

    stock_with_previous = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("140.00"),
    )
    assert stock_with_previous._is_close_to_two_hundred_day_average() is False

    stock_with_average = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        twoHundredDayAverage=Decimal("145.00"),
    )
    assert stock_with_average._is_close_to_two_hundred_day_average() is False


def test_is_close_to_two_hundred_day_average_returns_true_when_approaching_from_below_within_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("95.00"),
        twoHundredDayAverage=Decimal("105.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is True


def test_is_close_to_two_hundred_day_average_returns_true_when_approaching_from_above_within_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("105.00"),
        twoHundredDayAverage=Decimal("95.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is True


def test_is_close_to_two_hundred_day_average_returns_false_when_approaching_from_below_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("95.00"),
        twoHundredDayAverage=Decimal("106.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is False


def test_is_close_to_two_hundred_day_average_returns_false_when_approaching_from_above_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("105.00"),
        twoHundredDayAverage=Decimal("94.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is False


def test_is_close_to_two_hundred_day_average_returns_true_at_exact_threshold_from_below():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("95.00"),
        twoHundredDayAverage=Decimal("105.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is True


def test_is_close_to_two_hundred_day_average_returns_true_at_exact_threshold_from_above():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("105.00"),
        twoHundredDayAverage=Decimal("95.00"),
    )
    assert stock._is_close_to_two_hundred_day_average() is True


def test_is_close_to_two_hundred_day_average_returns_false_when_previous_close_on_same_side_as_price():
    stock_both_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("110.00"),
        previousClosePrice=Decimal("108.00"),
        twoHundredDayAverage=Decimal("100.00"),
    )
    assert stock_both_above._is_close_to_two_hundred_day_average() is False

    stock_both_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("90.00"),
        previousClosePrice=Decimal("92.00"),
        twoHundredDayAverage=Decimal("100.00"),
    )
    assert stock_both_below._is_close_to_two_hundred_day_average() is False


def test_is_close_to_two_hundred_day_average_returns_false_when_previous_equals_average():
    stock_current_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("103.00"),
        previousClosePrice=Decimal("100.00"),
        twoHundredDayAverage=Decimal("100.00"),
    )
    assert stock_current_above._is_close_to_two_hundred_day_average() is False

    stock_current_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("97.00"),
        previousClosePrice=Decimal("100.00"),
        twoHundredDayAverage=Decimal("100.00"),
    )
    assert stock_current_below._is_close_to_two_hundred_day_average() is False


def test_generate_notifications_adds_close_to_sma200_when_approaching_from_below():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("95.00"),
        twoHundredDayAverage=Decimal("103.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA200 in types


def test_generate_notifications_adds_close_to_sma200_when_approaching_from_above():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("105.00"),
        twoHundredDayAverage=Decimal("97.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA200 in types


def test_generate_notifications_does_not_add_close_to_sma200_when_beyond_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("95.00"),
        twoHundredDayAverage=Decimal("110.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA200 not in types


def test_generate_notifications_does_not_add_close_to_sma200_when_previous_close_on_same_side():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("110.00"),
        previousClosePrice=Decimal("108.00"),
        twoHundredDayAverage=Decimal("100.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    types = {n.type for n in stock.notifications}
    assert NotificationType.CLOSE_TO_SMA200 not in types


def test_has_crossed_two_hundred_day_average_returns_false_when_fields_are_missing():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))
    assert stock._has_crossed_two_hundred_day_average() is False

    stock_with_previous = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("130.00"),
    )
    assert stock_with_previous._has_crossed_two_hundred_day_average() is False

    stock_with_average = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock_with_average._has_crossed_two_hundred_day_average() is False


def test_has_crossed_two_hundred_day_average_detects_crossing_above():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("130.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock._has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_detects_crossing_below():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("130.00"),
        previousClosePrice=Decimal("150.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock._has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_returns_false_when_no_crossing():
    stock_both_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("148.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock_both_above._has_crossed_two_hundred_day_average() is False

    stock_both_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("130.00"),
        previousClosePrice=Decimal("135.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock_both_below._has_crossed_two_hundred_day_average() is False


def test_has_crossed_two_hundred_day_average_detects_crossing_above_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("140.00"),
        previousClosePrice=Decimal("130.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock._has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_detects_crossing_below_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("140.00"),
        previousClosePrice=Decimal("150.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock._has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_returns_false_when_previous_equals_average():
    stock_current_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("140.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock_current_above._has_crossed_two_hundred_day_average() is False

    stock_current_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("130.00"),
        previousClosePrice=Decimal("140.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock_current_below._has_crossed_two_hundred_day_average() is False


def test_change_percentage_from_previous_close_returns_none_when_previous_close_is_none():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))

    assert stock._change_percentage_from_previous_close() is None


def test_change_percentage_from_previous_close_returns_positive_percentage():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("100.00"),
    )

    assert stock._change_percentage_from_previous_close() == Decimal("50.00")


def test_change_percentage_from_previous_close_returns_negative_percentage():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("90.00"),
        previousClosePrice=Decimal("100.00"),
    )

    assert stock._change_percentage_from_previous_close() == Decimal("-10.00")


def test_change_percentage_from_previous_close_returns_zero_when_prices_are_equal():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("100.00"),
        previousClosePrice=Decimal("100.00"),
    )

    assert stock._change_percentage_from_previous_close() == Decimal("0.00")


def test_stock_optional_fields_default_to_none():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))

    assert stock.name is None
    assert stock.currency is None
    assert stock.previousClosePrice is None
    assert stock.openPrice is None
    assert stock.dayHigh is None
    assert stock.dayLow is None
    assert stock.fiftyDayAverage is None
    assert stock.twoHundredDayAverage is None
    assert stock.fiftyTwoWeekHigh is None
    assert stock.fiftyTwoWeekLow is None


def test_stock_notifications_defaults_to_empty_list():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))

    assert stock.notifications == []


def test_generate_notifications_adds_fifty_day_notification():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("140.00"),
        fiftyDayAverage=Decimal("145.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("130.00"),
        twoHundredDayAverage=Decimal("140.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("130.00"),
        fiftyDayAverage=Decimal("145.00"),
        twoHundredDayAverage=Decimal("140.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("148.00"),
        fiftyDayAverage=Decimal("120.00"),
        twoHundredDayAverage=Decimal("110.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN
    sma_types = {NotificationType.SMA50_CROSSED, NotificationType.SMA200_CROSSED}
    assert not any(n.type in sma_types for n in stock.notifications)


def test_is_market_state_open_returns_true_when_market_state_is_open():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        marketState=MarketState.OPEN,
    )

    assert stock._is_market_state_open() is True


def test_is_market_state_open_returns_false_when_market_state_is_closed():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        marketState=MarketState.CLOSED,
    )

    assert stock._is_market_state_open() is False


def test_is_market_state_open_returns_false_when_market_state_is_none():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))

    assert stock._is_market_state_open() is False


def test_generate_notifications_adds_regular_market_open_notification():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        openPrice=Decimal("149.75"),
        previousClosePrice=Decimal("148.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN


def test_generate_notifications_adds_regular_market_open_with_current_price_fallback():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("148.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN


def test_generate_notifications_does_not_add_regular_market_open_when_market_closed():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        openPrice=Decimal("149.75"),
        previousClosePrice=Decimal("148.00"),
        marketState=MarketState.CLOSED,
    )

    stock.generate_notifications()

    assert stock.notifications == []


def test_is_market_state_post_returns_true_when_market_state_is_post():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        marketState=MarketState.POST,
    )

    assert stock._is_market_state_post() is True


def test_is_market_state_post_returns_false_for_other_states():
    for state in [MarketState.OPEN, MarketState.PRE, MarketState.CLOSED]:
        stock = Stock(
            symbol="AAPL",
            currentPrice=Decimal("150.00"),
            marketState=state,
        )
        assert stock._is_market_state_post() is False


def test_is_market_state_post_returns_false_when_market_state_is_none():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))

    assert stock._is_market_state_post() is False


def test_generate_notifications_adds_regular_market_closed_when_post():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        marketState=MarketState.POST,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_CLOSED


def test_generate_notifications_adds_twenty_percent_increase():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("121.00"),
        previousClosePrice=Decimal("100.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("116.00"),
        previousClosePrice=Decimal("100.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("111.00"),
        previousClosePrice=Decimal("100.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("106.00"),
        previousClosePrice=Decimal("100.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("79.00"),
        previousClosePrice=Decimal("100.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("84.00"),
        previousClosePrice=Decimal("100.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("89.00"),
        previousClosePrice=Decimal("100.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("94.00"),
        previousClosePrice=Decimal("100.00"),
        marketState=MarketState.OPEN,
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
        currentPrice=Decimal("104.00"),
        previousClosePrice=Decimal("100.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN


def test_generate_notifications_percentage_at_exact_threshold():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("105.00"),
        previousClosePrice=Decimal("100.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {
        NotificationType.REGULAR_MARKET_OPEN,
        NotificationType.FIVE_PERCENT_INCREASE,
    }


def test_generate_new_52_week_high_notification_does_not_add_when_past_stock_is_none():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("200.00"))

    stock._generate_new_52_week_high_notification(None)

    assert stock.notifications == []


def test_generate_new_52_week_high_notification_does_not_add_when_past_stock_has_no_52_week_high():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("200.00"))
    past_stock = Stock(symbol="AAPL", currentPrice=Decimal("180.00"))

    stock._generate_new_52_week_high_notification(past_stock)

    assert stock.notifications == []


def test_generate_new_52_week_high_notification_does_not_add_when_current_price_equals_past_stock_52_week_high():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("180.00"))
    past_stock = Stock(
        symbol="AAPL", currentPrice=Decimal("170.00"), fiftyTwoWeekHigh=Decimal("180.00")
    )

    stock._generate_new_52_week_high_notification(past_stock)

    assert stock.notifications == []


def test_generate_new_52_week_high_notification_does_not_add_when_current_price_below_past_stock_52_week_high():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("170.00"))
    past_stock = Stock(
        symbol="AAPL", currentPrice=Decimal("160.00"), fiftyTwoWeekHigh=Decimal("180.00")
    )

    stock._generate_new_52_week_high_notification(past_stock)

    assert stock.notifications == []


def test_generate_new_52_week_high_notification_adds_notification_when_current_price_exceeds_past_stock_52_week_high():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("200.00"))
    past_stock = Stock(
        symbol="AAPL", currentPrice=Decimal("170.00"), fiftyTwoWeekHigh=Decimal("180.00")
    )

    stock._generate_new_52_week_high_notification(past_stock)

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.NEW_52_WEEK_HIGH


def test_generate_new_52_week_low_notification_does_not_add_when_past_stock_is_none():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("100.00"))

    stock._generate_new_52_week_low_notification(None)

    assert stock.notifications == []


def test_generate_new_52_week_low_notification_does_not_add_when_past_stock_has_no_52_week_low():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("100.00"))
    past_stock = Stock(symbol="AAPL", currentPrice=Decimal("120.00"))

    stock._generate_new_52_week_low_notification(past_stock)

    assert stock.notifications == []


def test_generate_new_52_week_low_notification_does_not_add_when_current_price_equals_past_stock_52_week_low():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("120.00"))
    past_stock = Stock(
        symbol="AAPL", currentPrice=Decimal("130.00"), fiftyTwoWeekLow=Decimal("120.00")
    )

    stock._generate_new_52_week_low_notification(past_stock)

    assert stock.notifications == []


def test_generate_new_52_week_low_notification_does_not_add_when_current_price_above_past_stock_52_week_low():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("130.00"))
    past_stock = Stock(
        symbol="AAPL", currentPrice=Decimal("140.00"), fiftyTwoWeekLow=Decimal("120.00")
    )

    stock._generate_new_52_week_low_notification(past_stock)

    assert stock.notifications == []


def test_generate_new_52_week_low_notification_adds_notification_when_current_price_falls_below_past_stock_52_week_low():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("100.00"))
    past_stock = Stock(
        symbol="AAPL", currentPrice=Decimal("130.00"), fiftyTwoWeekLow=Decimal("120.00")
    )

    stock._generate_new_52_week_low_notification(past_stock)

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.NEW_52_WEEK_LOW


def test_generate_notifications_no_percentage_when_previous_close_none():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN

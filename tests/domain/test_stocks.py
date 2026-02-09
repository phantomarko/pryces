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
    assert stock.has_crossed_fifty_day_average() is False

    stock_with_previous = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("140.00"),
    )
    assert stock_with_previous.has_crossed_fifty_day_average() is False

    stock_with_average = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_with_average.has_crossed_fifty_day_average() is False


def test_has_crossed_fifty_day_average_detects_crossing_above():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("140.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock.has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_detects_crossing_below():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("140.00"),
        previousClosePrice=Decimal("150.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock.has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_returns_false_when_no_crossing():
    stock_both_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("148.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_both_above.has_crossed_fifty_day_average() is False

    stock_both_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("140.00"),
        previousClosePrice=Decimal("142.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_both_below.has_crossed_fifty_day_average() is False


def test_has_crossed_fifty_day_average_detects_crossing_above_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("145.00"),
        previousClosePrice=Decimal("140.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock.has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_detects_crossing_below_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("145.00"),
        previousClosePrice=Decimal("150.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock.has_crossed_fifty_day_average() is True


def test_has_crossed_fifty_day_average_returns_false_when_previous_equals_average():
    stock_current_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("145.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_current_above.has_crossed_fifty_day_average() is False

    stock_current_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("140.00"),
        previousClosePrice=Decimal("145.00"),
        fiftyDayAverage=Decimal("145.00"),
    )
    assert stock_current_below.has_crossed_fifty_day_average() is False


def test_has_crossed_two_hundred_day_average_returns_false_when_fields_are_missing():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))
    assert stock.has_crossed_two_hundred_day_average() is False

    stock_with_previous = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("130.00"),
    )
    assert stock_with_previous.has_crossed_two_hundred_day_average() is False

    stock_with_average = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock_with_average.has_crossed_two_hundred_day_average() is False


def test_has_crossed_two_hundred_day_average_detects_crossing_above():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("130.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock.has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_detects_crossing_below():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("130.00"),
        previousClosePrice=Decimal("150.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock.has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_returns_false_when_no_crossing():
    stock_both_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("148.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock_both_above.has_crossed_two_hundred_day_average() is False

    stock_both_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("130.00"),
        previousClosePrice=Decimal("135.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock_both_below.has_crossed_two_hundred_day_average() is False


def test_has_crossed_two_hundred_day_average_detects_crossing_above_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("140.00"),
        previousClosePrice=Decimal("130.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock.has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_detects_crossing_below_when_current_equals_average():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("140.00"),
        previousClosePrice=Decimal("150.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock.has_crossed_two_hundred_day_average() is True


def test_has_crossed_two_hundred_day_average_returns_false_when_previous_equals_average():
    stock_current_above = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("140.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock_current_above.has_crossed_two_hundred_day_average() is False

    stock_current_below = Stock(
        symbol="AAPL",
        currentPrice=Decimal("130.00"),
        previousClosePrice=Decimal("140.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )
    assert stock_current_below.has_crossed_two_hundred_day_average() is False


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


def test_generate_milestones_notifications_adds_fifty_day_notification():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("140.00"),
        fiftyDayAverage=Decimal("145.00"),
    )

    stock.generate_milestones_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.SMA50_CROSSED


def test_generate_milestones_notifications_adds_two_hundred_day_notification():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("130.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )

    stock.generate_milestones_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.SMA200_CROSSED


def test_generate_milestones_notifications_adds_both_notifications():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("130.00"),
        fiftyDayAverage=Decimal("145.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )

    stock.generate_milestones_notifications()

    assert len(stock.notifications) == 2
    types = {n.type for n in stock.notifications}
    assert types == {NotificationType.SMA50_CROSSED, NotificationType.SMA200_CROSSED}


def test_generate_milestones_notifications_adds_no_notifications_when_no_crossing():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        previousClosePrice=Decimal("148.00"),
        fiftyDayAverage=Decimal("145.00"),
        twoHundredDayAverage=Decimal("140.00"),
    )

    stock.generate_milestones_notifications()

    assert stock.notifications == []


def test_is_market_state_open_returns_true_when_market_state_is_open():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        marketState=MarketState.OPEN,
    )

    assert stock.is_market_state_open() is True


def test_is_market_state_open_returns_false_when_market_state_is_closed():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        marketState=MarketState.CLOSED,
    )

    assert stock.is_market_state_open() is False


def test_is_market_state_open_returns_false_when_market_state_is_none():
    stock = Stock(symbol="AAPL", currentPrice=Decimal("150.00"))

    assert stock.is_market_state_open() is False


def test_generate_milestones_notifications_adds_regular_market_open_notification():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        openPrice=Decimal("149.75"),
        previousClosePrice=Decimal("148.00"),
        marketState=MarketState.OPEN,
    )

    stock.generate_milestones_notifications()

    assert len(stock.notifications) == 1
    assert stock.notifications[0].type == NotificationType.REGULAR_MARKET_OPEN


def test_generate_milestones_notifications_does_not_add_regular_market_open_when_market_closed():
    stock = Stock(
        symbol="AAPL",
        currentPrice=Decimal("150.00"),
        openPrice=Decimal("149.75"),
        previousClosePrice=Decimal("148.00"),
        marketState=MarketState.CLOSED,
    )

    stock.generate_milestones_notifications()

    assert stock.notifications == []

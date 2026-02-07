from decimal import Decimal

from pryces.domain.stocks import Stock


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

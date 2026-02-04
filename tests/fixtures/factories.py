"""Test factories for creating test data objects."""

from decimal import Decimal

from pryces.application.providers import StockPriceResponse


def create_stock_price(
    symbol: str = "AAPL",
    current_price: Decimal = Decimal("150.00"),
    **overrides
) -> StockPriceResponse:
    """Create a StockPriceResponse with sensible defaults for testing.

    Required fields (symbol, currentPrice) have defaults but can be overridden.
    All optional fields are computed from current_price but can be overridden.

    Args:
        symbol: Stock ticker symbol (default: "AAPL")
        current_price: Current stock price (default: 150.00)
        **overrides: Override any field (name, currency, previousClosePrice, etc.)

    Returns:
        StockPriceResponse with realistic test data

    Examples:
        # Use all defaults
        stock = create_stock_price()

        # Custom symbol and price
        stock = create_stock_price("GOOGL", Decimal("2800.00"))

        # Override specific fields
        stock = create_stock_price("TSLA", Decimal("200.00"),
                                   name="Tesla, Inc.",
                                   currency="EUR")

        # Create minimal object (only required fields)
        stock = create_stock_price("MSFT", Decimal("350.00"),
                                   name=None,
                                   currency=None,
                                   previousClosePrice=None,
                                   openPrice=None,
                                   dayHigh=None,
                                   dayLow=None,
                                   fiftyDayAverage=None,
                                   twoHundredDayAverage=None,
                                   fiftyTwoWeekHigh=None,
                                   fiftyTwoWeekLow=None)
    """
    defaults = {
        "name": f"{symbol} Inc.",
        "currency": "USD",
        "previousClosePrice": current_price * Decimal("0.99"),
        "openPrice": current_price * Decimal("0.995"),
        "dayHigh": current_price * Decimal("1.01"),
        "dayLow": current_price * Decimal("0.98"),
        "fiftyDayAverage": current_price * Decimal("0.97"),
        "twoHundredDayAverage": current_price * Decimal("0.93"),
        "fiftyTwoWeekHigh": current_price * Decimal("1.20"),
        "fiftyTwoWeekLow": current_price * Decimal("0.80"),
    }

    return StockPriceResponse(
        symbol=symbol,
        currentPrice=current_price,
        **{**defaults, **overrides}
    )

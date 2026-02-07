from decimal import Decimal

from pryces.application.interfaces import StockPrice


def create_stock_price(
    symbol: str = "AAPL", current_price: Decimal = Decimal("150.00"), **overrides
) -> StockPrice:
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

    return StockPrice(symbol=symbol, currentPrice=current_price, **{**defaults, **overrides})

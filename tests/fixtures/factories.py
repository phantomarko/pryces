from decimal import Decimal

from pryces.application.dtos import StockDTO
from pryces.domain.stocks import Stock


def create_stock(
    symbol: str = "AAPL", current_price: Decimal = Decimal("150.00"), **overrides
) -> Stock:
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

    return Stock(symbol=symbol, currentPrice=current_price, **{**defaults, **overrides})


def create_stock_crossing_fifty_day(symbol: str = "AAPL") -> Stock:
    return create_stock(
        symbol,
        Decimal("101"),
        previousClosePrice=Decimal("99"),
        fiftyDayAverage=Decimal("100"),
    )


def create_stock_crossing_two_hundred_day(symbol: str = "AAPL") -> Stock:
    return create_stock(
        symbol,
        Decimal("201"),
        previousClosePrice=Decimal("199"),
        twoHundredDayAverage=Decimal("200"),
    )


def create_stock_crossing_both_averages(symbol: str = "AAPL") -> Stock:
    return create_stock(
        symbol,
        Decimal("101"),
        previousClosePrice=Decimal("99"),
        fiftyDayAverage=Decimal("100"),
        twoHundredDayAverage=Decimal("100"),
    )


def create_stock_no_crossing(symbol: str = "AAPL") -> Stock:
    return create_stock(
        symbol,
        Decimal("150"),
        previousClosePrice=Decimal("149"),
        fiftyDayAverage=Decimal("130"),
        twoHundredDayAverage=Decimal("120"),
    )


def create_stock_dto(
    symbol: str = "AAPL", current_price: Decimal = Decimal("150.00"), **overrides
) -> StockDTO:
    return StockDTO.from_stock(create_stock(symbol, current_price, **overrides))

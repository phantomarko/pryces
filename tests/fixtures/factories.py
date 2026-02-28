from decimal import Decimal

from pryces.application.dtos import StockDTO
from pryces.domain.stocks import MarketState, Stock


def create_stock(
    symbol: str = "AAPL", current_price: Decimal = Decimal("150.00"), **overrides
) -> Stock:
    defaults = {
        "name": f"{symbol} Inc.",
        "currency": "USD",
        "previous_close_price": current_price * Decimal("0.99"),
        "open_price": current_price * Decimal("0.995"),
        "day_high": current_price * Decimal("1.01"),
        "day_low": current_price * Decimal("0.98"),
        "fifty_day_average": current_price * Decimal("0.97"),
        "two_hundred_day_average": current_price * Decimal("0.93"),
        "fifty_two_week_high": current_price * Decimal("1.20"),
        "fifty_two_week_low": current_price * Decimal("0.80"),
        "market_state": MarketState.OPEN,
        "price_delay_in_minutes": 0,
    }

    return Stock(symbol=symbol, current_price=current_price, **{**defaults, **overrides})


def create_stock_crossing_fifty_day(symbol: str = "AAPL") -> Stock:
    return create_stock(
        symbol,
        Decimal("101"),
        previous_close_price=Decimal("99"),
        fifty_day_average=Decimal("100"),
    )


def create_stock_crossing_two_hundred_day(symbol: str = "AAPL") -> Stock:
    return create_stock(
        symbol,
        Decimal("201"),
        previous_close_price=Decimal("199"),
        two_hundred_day_average=Decimal("200"),
    )


def create_stock_crossing_both_averages(symbol: str = "AAPL") -> Stock:
    return create_stock(
        symbol,
        Decimal("101"),
        previous_close_price=Decimal("99"),
        fifty_day_average=Decimal("100"),
        two_hundred_day_average=Decimal("100"),
    )


def create_stock_no_crossing(symbol: str = "AAPL") -> Stock:
    return create_stock(
        symbol,
        Decimal("150"),
        previous_close_price=Decimal("149"),
        fifty_day_average=Decimal("130"),
        two_hundred_day_average=Decimal("120"),
    )


def create_stock_dto(
    symbol: str = "AAPL", current_price: Decimal = Decimal("150.00"), **overrides
) -> StockDTO:
    return StockDTO.from_stock(create_stock(symbol, current_price, **overrides))

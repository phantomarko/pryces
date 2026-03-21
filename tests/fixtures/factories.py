from decimal import Decimal

from pryces.application.dtos import StockDTO
from pryces.domain.stocks import InstrumentType, MarketState, Stock


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
        "market_cap": Decimal("2500000000000"),
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


def make_stock(
    *,
    symbol: str = "AAPL",
    current_price: str | Decimal = "150.00",
    previous_close_price: str | Decimal | None = None,
    open_price: str | Decimal | None = None,
    day_high: str | Decimal | None = None,
    day_low: str | Decimal | None = None,
    fifty_day_average: str | Decimal | None = None,
    two_hundred_day_average: str | Decimal | None = None,
    fifty_two_week_high: str | Decimal | None = None,
    fifty_two_week_low: str | Decimal | None = None,
    market_cap: str | Decimal | None = None,
    market_state: MarketState | None = MarketState.OPEN,
    price_delay_in_minutes: int | None = None,
    kind: InstrumentType | None = None,
) -> Stock:
    def d(v):
        return Decimal(v) if isinstance(v, str) else v

    return Stock(
        symbol=symbol,
        current_price=d(current_price),
        previous_close_price=d(previous_close_price),
        open_price=d(open_price),
        day_high=d(day_high),
        day_low=d(day_low),
        fifty_day_average=d(fifty_day_average),
        two_hundred_day_average=d(two_hundred_day_average),
        fifty_two_week_high=d(fifty_two_week_high),
        fifty_two_week_low=d(fifty_two_week_low),
        market_cap=d(market_cap),
        market_state=market_state,
        price_delay_in_minutes=price_delay_in_minutes,
        kind=kind,
    )


def open_stock_after_burn(**kwargs) -> Stock:
    """Constructs a stock and burns the market-open notification cycle."""
    stock = make_stock(**kwargs)
    stock.generate_notifications()
    stock.drain_notifications()
    return stock


def generate_and_drain(stock: Stock) -> list[str]:
    stock.generate_notifications()
    return stock.drain_notifications()


def open_stock_ready_for_target(entry_price: str, target: str, hit_price: str) -> Stock:
    """Stock that has been market-open burned, target set, and updated to hit price."""
    stock = open_stock_after_burn(current_price=entry_price, previous_close_price="195.00")
    stock.sync_targets([Decimal(target)])
    stock.update(make_stock(current_price=hit_price, previous_close_price="195.00"))
    return stock

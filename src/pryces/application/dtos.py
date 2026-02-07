from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal

from pryces.domain.stocks import Stock


@dataclass(frozen=True)
class StockPriceDTO:
    symbol: str
    currentPrice: Decimal
    name: str | None = None
    currency: str | None = None
    previousClosePrice: Decimal | None = None
    openPrice: Decimal | None = None
    dayHigh: Decimal | None = None
    dayLow: Decimal | None = None
    fiftyDayAverage: Decimal | None = None
    twoHundredDayAverage: Decimal | None = None
    fiftyTwoWeekHigh: Decimal | None = None
    fiftyTwoWeekLow: Decimal | None = None

    def to_stock(self) -> Stock:
        return Stock(**asdict(self))

    @staticmethod
    def from_stock(stock: Stock) -> StockPriceDTO:
        data = asdict(stock)
        data.pop("notifications", None)
        return StockPriceDTO(**data)

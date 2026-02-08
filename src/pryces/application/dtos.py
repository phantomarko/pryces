from __future__ import annotations

from dataclasses import dataclass, field
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
    notifications: list[str] = field(default_factory=list)

    @staticmethod
    def from_stock(stock: Stock) -> StockPriceDTO:
        return StockPriceDTO(
            symbol=stock.symbol,
            currentPrice=stock.currentPrice,
            name=stock.name,
            currency=stock.currency,
            previousClosePrice=stock.previousClosePrice,
            openPrice=stock.openPrice,
            dayHigh=stock.dayHigh,
            dayLow=stock.dayLow,
            fiftyDayAverage=stock.fiftyDayAverage,
            twoHundredDayAverage=stock.twoHundredDayAverage,
            fiftyTwoWeekHigh=stock.fiftyTwoWeekHigh,
            fiftyTwoWeekLow=stock.fiftyTwoWeekLow,
            notifications=[n.message for n in stock.notifications],
        )

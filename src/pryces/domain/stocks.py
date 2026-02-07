from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Stock:
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

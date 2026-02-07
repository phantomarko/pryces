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

    def has_crossed_fifty_day_average(self) -> bool:
        if self.previousClosePrice is None or self.fiftyDayAverage is None:
            return False

        crossed_above = (
            self.previousClosePrice < self.fiftyDayAverage
            and self.currentPrice >= self.fiftyDayAverage
        )
        crossed_below = (
            self.previousClosePrice > self.fiftyDayAverage
            and self.currentPrice <= self.fiftyDayAverage
        )

        return crossed_above or crossed_below

    def has_crossed_two_hundred_day_average(self) -> bool:
        if self.previousClosePrice is None or self.twoHundredDayAverage is None:
            return False

        crossed_above = (
            self.previousClosePrice < self.twoHundredDayAverage
            and self.currentPrice >= self.twoHundredDayAverage
        )
        crossed_below = (
            self.previousClosePrice > self.twoHundredDayAverage
            and self.currentPrice <= self.twoHundredDayAverage
        )

        return crossed_above or crossed_below

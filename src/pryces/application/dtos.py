from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from pryces.domain.notifications import Notification
from pryces.domain.stocks import Stock


@dataclass(frozen=True, slots=True)
class NotificationDTO:
    type: str
    message: str

    @staticmethod
    def from_notification(notification: Notification) -> NotificationDTO:
        return NotificationDTO(
            type=notification.type.value,
            message=notification.message,
        )


@dataclass(frozen=True, slots=True)
class StockDTO:
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
    marketState: str | None = None
    notifications: list[NotificationDTO] = field(default_factory=list)

    @staticmethod
    def from_stock(stock: Stock) -> StockDTO:
        return StockDTO(
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
            marketState=stock.marketState.value if stock.marketState else None,
            notifications=[NotificationDTO.from_notification(n) for n in stock.notifications],
        )

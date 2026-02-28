import logging
from datetime import datetime
from decimal import Decimal

from ..application.repositories import (
    MarketTransitionRepository,
    NotificationRepository,
    StockRepository,
    TargetPriceRepository,
)
from ..domain.notifications import Notification, NotificationType
from ..domain.target_prices import TargetPrice
from ..domain.stocks import Stock


class InMemoryNotificationRepository(NotificationRepository):
    def __init__(self) -> None:
        self._store: dict[str, dict[str, bool]] = {}

    def save(self, symbol: str, notification: Notification) -> None:
        if symbol not in self._store:
            self._store[symbol] = {}
        self._store[symbol][notification.type.value] = True

    def exists_by_type(self, symbol: str, notification_type: NotificationType) -> bool:
        if symbol not in self._store:
            return False
        return notification_type.value in self._store[symbol]


class InMemoryStockRepository(StockRepository):
    def __init__(self) -> None:
        self._store: dict[str, Stock] = {}

    def save_batch(self, stocks: list[Stock]) -> None:
        for stock in stocks:
            self._store[stock.symbol] = stock

    def get(self, symbol: str) -> Stock | None:
        return self._store.get(symbol)


class InMemoryMarketTransitionRepository(MarketTransitionRepository):
    def __init__(self) -> None:
        self._store: dict[str, datetime] = {}

    def save(self, symbol: str, transition_time: datetime) -> None:
        self._store[symbol] = transition_time

    def get(self, symbol: str) -> datetime | None:
        return self._store.get(symbol)

    def delete(self, symbol: str) -> None:
        self._store.pop(symbol, None)


class InMemoryTargetPriceRepository(TargetPriceRepository):
    def __init__(self) -> None:
        self._store: dict[str, dict[Decimal, TargetPrice]] = {}
        self._logger = logging.getLogger(__name__)

    def get_by_symbol(self, symbols: list[str]) -> list[TargetPrice]:
        return [pt for s in symbols for pt in self._store.get(s, {}).values()]

    def save(self, price_target: TargetPrice) -> None:
        if price_target.symbol not in self._store:
            self._store[price_target.symbol] = {}
        self._store[price_target.symbol][price_target.target] = price_target
        entry = price_target.entry if price_target.entry is not None else "NULL"
        self._logger.info(
            f"Target price saved: {price_target.symbol} / target={price_target.target} / entry={entry}"
        )

    def delete(self, price_target: TargetPrice) -> None:
        symbol_store = self._store.get(price_target.symbol)
        if symbol_store is not None:
            symbol_store.pop(price_target.target, None)
        self._logger.info(
            f"Target price deleted: {price_target.symbol} / target={price_target.target}"
        )

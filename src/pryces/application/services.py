from datetime import datetime
from decimal import Decimal
from typing import Callable

from pryces.domain.notification_formatter import NotificationFormatter
from pryces.domain.stocks import Stock

from .interfaces import MessageSender, StockProvider, StockRepository


class NotificationService:
    def __init__(
        self,
        message_sender: MessageSender,
        formatter: NotificationFormatter,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._message_sender = message_sender
        self._formatter = formatter
        self._clock = clock

    def send_stock_notifications(self, stock: Stock) -> None:
        stock.generate_notifications(now=self._clock())
        for message in stock.drain_notifications(self._formatter):
            self._message_sender.send_message(message)


class StockSynchronizer:
    def __init__(
        self,
        provider: StockProvider,
        stock_repository: StockRepository,
    ) -> None:
        self._provider = provider
        self._stock_repository = stock_repository

    def fetch_and_sync(self, symbols: list[str], targets: dict[str, list[Decimal]]) -> list[Stock]:
        fresh_stocks = self._provider.get_stocks(symbols)
        synced: list[Stock] = []

        for fresh_stock in fresh_stocks:
            existing = self._stock_repository.get(fresh_stock.symbol)
            if existing is not None:
                existing.update(fresh_stock)
                stock = existing
            else:
                stock = fresh_stock

            stock.sync_targets(targets.get(stock.symbol, []))
            synced.append(stock)

        return synced

    def persist(self, stocks: list[Stock]) -> None:
        self._stock_repository.save_batch(stocks)

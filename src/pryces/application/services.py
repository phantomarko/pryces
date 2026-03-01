from datetime import datetime
from decimal import Decimal
from typing import Callable

from pryces.domain.stocks import Stock

from .interfaces import MarketTransitionRepository, MessageSender, StockProvider, StockRepository


class NotificationService:
    def __init__(
        self,
        message_sender: MessageSender,
        transition_repository: MarketTransitionRepository,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._message_sender = message_sender
        self._transition_repository = transition_repository
        self._clock = clock

    def _is_in_delay_window(self, stock: Stock) -> bool:
        if not stock.price_delay_in_minutes:
            return False
        if stock.is_market_state_transition():
            self._transition_repository.save(stock.symbol, self._clock())
            return True
        transition_time = self._transition_repository.get(stock.symbol)
        if transition_time is None:
            return False
        elapsed_minutes = (self._clock() - transition_time).total_seconds() / 60
        if elapsed_minutes < stock.price_delay_in_minutes:
            return True
        self._transition_repository.delete(stock.symbol)
        return False

    def send_stock_notifications(self, stock: Stock) -> None:
        if self._is_in_delay_window(stock):
            return

        messages = stock.generate_notifications()

        for message in messages:
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

from datetime import datetime
from typing import Callable

from pryces.domain.notifications import Notification
from pryces.domain.stocks import MarketState, Stock

from .interfaces import MarketTransitionRepository, MessageSender, NotificationRepository


class NotificationService:
    def __init__(
        self,
        message_sender: MessageSender,
        repository: NotificationRepository,
        transition_repository: MarketTransitionRepository,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._message_sender = message_sender
        self._notification_repository = repository
        self._transition_repository = transition_repository
        self._clock = clock

    def _is_market_state_transition(self, stock: Stock, past_stock: Stock | None) -> bool:
        if past_stock is None:
            return False
        return past_stock.marketState != stock.marketState and stock.marketState in (
            MarketState.OPEN,
            MarketState.POST,
        )

    def _is_in_delay_window(self, stock: Stock, past_stock: Stock | None) -> bool:
        if not stock.priceDelayInMinutes:
            return False
        if self._is_market_state_transition(stock, past_stock):
            self._transition_repository.save(stock.symbol, self._clock())
            return True
        transition_time = self._transition_repository.get(stock.symbol)
        if transition_time is None:
            return False
        elapsed_minutes = (self._clock() - transition_time).total_seconds() / 60
        if elapsed_minutes < stock.priceDelayInMinutes:
            return True
        self._transition_repository.delete(stock.symbol)
        return False

    def send_stock_notifications(
        self, stock: Stock, past_stock: Stock | None
    ) -> list[Notification]:
        if self._is_in_delay_window(stock, past_stock):
            return []

        stock.generate_notifications(past_stock)
        sent: list[Notification] = []

        for notification in stock.notifications:
            if self._notification_repository.exists_by_type(stock.symbol, notification.type):
                continue

            self._message_sender.send_message(notification.message)
            self._notification_repository.save(stock.symbol, notification)
            sent.append(notification)

        return sent

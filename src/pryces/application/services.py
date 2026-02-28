from datetime import datetime
from typing import Callable

from pryces.domain.notifications import Notification
from pryces.domain.stocks import Stock
from pryces.domain.target_prices import TargetPrice

from .repositories import MarketTransitionRepository, NotificationRepository
from .senders import MessageSender


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

    def send_stock_notifications(self, stock: Stock) -> list[Notification]:
        if self._is_in_delay_window(stock):
            return []

        stock.generate_notifications()
        sent: list[Notification] = []

        for notification in stock.notifications:
            if self._notification_repository.exists_by_type(stock.symbol, notification.type):
                continue

            self._message_sender.send_message(notification.message)
            self._notification_repository.save(stock.symbol, notification)
            sent.append(notification)

        return sent

    def send_stock_targets_notifications(
        self, stock: Stock, targets: list[TargetPrice]
    ) -> list[TargetPrice]:
        triggered: list[TargetPrice] = []

        for target in targets:
            notification = target.generate_notification(stock)
            if notification is not None:
                self._message_sender.send_message(notification.message)
                triggered.append(target)

        return triggered

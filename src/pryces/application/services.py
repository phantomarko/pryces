from datetime import datetime
from typing import Callable

from pryces.domain.stocks import Stock
from pryces.domain.target_prices import TargetPrice

from .repositories import MarketTransitionRepository
from .senders import MessageSender


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

    def send_stock_notifications(
        self, stock: Stock, targets: list[TargetPrice]
    ) -> list[TargetPrice]:
        if self._is_in_delay_window(stock):
            return []

        result = stock.generate_notifications(targets)

        for notification in result.new_notifications:
            self._message_sender.send_message(notification.message)

        return result.triggered_targets

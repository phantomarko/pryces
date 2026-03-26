from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from pryces.domain.notifications import (
    MILESTONE_NOTIFICATION_TYPES,
    STANDALONE_NOTIFICATION_TYPES,
    Notification,
    NotificationType,
)
from pryces.domain.utils import _calculate_percentage_change


@dataclass(frozen=True, slots=True)
class StockContext:
    symbol: str
    current_price: Decimal
    previous_close_price: Decimal | None


class NotificationFormatter(ABC):
    @abstractmethod
    def format(self, notifications: list[Notification], context: StockContext) -> list[str]:
        pass


class ConsolidatingNotificationFormatter(NotificationFormatter):
    def format(self, notifications: list[Notification], context: StockContext) -> list[str]:
        standalone: list[Notification] = []
        consolidatable: list[Notification] = []

        for n in notifications:
            if n.type in STANDALONE_NOTIFICATION_TYPES:
                standalone.append(n)
            else:
                consolidatable.append(n)

        messages: list[str] = []

        if consolidatable:
            header = self._pick_header(consolidatable, context)
            body = [n.message for n in consolidatable if n is not header]
            lines = [header.message] + body
            messages.append("\n".join(lines))

        for n in standalone:
            messages.append(n.message)

        return messages

    def _pick_header(
        self, consolidatable: list[Notification], context: StockContext
    ) -> Notification:
        for n in consolidatable:
            if n.type == NotificationType.REGULAR_MARKET_OPEN:
                return n
        for n in consolidatable:
            if (
                n.type != NotificationType.REGULAR_MARKET_OPEN
                and n.type not in MILESTONE_NOTIFICATION_TYPES
            ):
                return n
        return self._generate_fallback_header(context)

    def _generate_fallback_header(self, context: StockContext) -> Notification:
        if context.previous_close_price is None:
            return Notification.create_plain_header(context.symbol, context.current_price)
        change_pct = _calculate_percentage_change(
            context.current_price, context.previous_close_price
        )
        return Notification.create_percentage_change(
            NotificationType.LEVEL_1_INCREASE,
            context.symbol,
            context.current_price,
            change_pct,
        )

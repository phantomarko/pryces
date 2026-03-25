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
        milestones: list[Notification] = []
        header_only: list[Notification] = []

        for n in notifications:
            if n.type in STANDALONE_NOTIFICATION_TYPES:
                standalone.append(n)
            elif n.type in MILESTONE_NOTIFICATION_TYPES:
                milestones.append(n)
            else:
                header_only.append(n)

        messages: list[str] = []

        if milestones:
            header = self._build_consolidation_header(header_only, context)
            lines = [header]
            for m in milestones:
                lines.append(m.message)
            messages.append("\n".join(lines))
        else:
            for n in header_only:
                messages.append(n.message)

        for n in standalone:
            messages.append(n.message)

        return messages

    def _build_consolidation_header(
        self, header_only: list[Notification], context: StockContext
    ) -> str:
        for n in header_only:
            return n.message
        if context.previous_close_price is None:
            return f"{context.symbol} at {context.current_price}"
        change_pct = _calculate_percentage_change(
            context.current_price, context.previous_close_price
        )
        return Notification.create_percentage_change(
            NotificationType.LEVEL_1_INCREASE,
            context.symbol,
            context.current_price,
            change_pct,
        ).message

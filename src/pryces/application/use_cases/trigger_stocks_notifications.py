from dataclasses import dataclass
from enum import Enum

from ..dtos import NotificationDTO
from ..interfaces import StockProvider
from ..services import NotificationService


class TriggerType(str, Enum):
    MILESTONES = "MILESTONES"


@dataclass(frozen=True)
class TriggerStocksNotificationsRequest:
    type: TriggerType
    symbols: list[str]


class TriggerStocksNotifications:
    def __init__(self, provider: StockProvider, notification_service: NotificationService) -> None:
        self._provider = provider
        self._notification_service = notification_service

    def handle(self, request: TriggerStocksNotificationsRequest) -> list[NotificationDTO]:
        stocks = self._provider.get_stocks(request.symbols)
        sent_notifications: list[NotificationDTO] = []

        if request.type == TriggerType.MILESTONES:
            for stock in stocks:
                stock.generate_milestones_notifications()
                sent = self._notification_service.send_stock_notifications(stock)
                sent_notifications.extend(NotificationDTO.from_notification(n) for n in sent)

        return sent_notifications

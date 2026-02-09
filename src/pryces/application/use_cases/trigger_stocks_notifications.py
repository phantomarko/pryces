from dataclasses import dataclass

from ..dtos import NotificationDTO
from ..interfaces import StockProvider
from ..services import NotificationService


@dataclass(frozen=True)
class TriggerStocksNotificationsRequest:
    symbols: list[str]


class TriggerStocksNotifications:
    def __init__(self, provider: StockProvider, notification_service: NotificationService) -> None:
        self._provider = provider
        self._notification_service = notification_service

    def handle(self, request: TriggerStocksNotificationsRequest) -> list[NotificationDTO]:
        stocks = self._provider.get_stocks(request.symbols)
        sent_notifications: list[NotificationDTO] = []

        for stock in stocks:
            sent = self._notification_service.send_stock_notifications(stock)
            sent_notifications.extend(NotificationDTO.from_notification(n) for n in sent)

        return sent_notifications

from dataclasses import dataclass

from ..interfaces import StockProvider, StockRepository
from ..services import NotificationService


@dataclass(frozen=True)
class TriggerStocksNotificationsRequest:
    symbols: list[str]


class TriggerStocksNotifications:
    def __init__(
        self,
        provider: StockProvider,
        notification_service: NotificationService,
        stock_repository: StockRepository,
    ) -> None:
        self._provider = provider
        self._notification_service = notification_service
        self._stock_repository = stock_repository

    def handle(self, request: TriggerStocksNotificationsRequest) -> None:
        stocks = self._provider.get_stocks(request.symbols)

        for stock in stocks:
            self._notification_service.send_stock_notifications(stock)

        self._stock_repository.save_batch(stocks)

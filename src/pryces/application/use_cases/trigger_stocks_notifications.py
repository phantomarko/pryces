from dataclasses import dataclass, field
from decimal import Decimal

from ..dtos import TargetPriceDTO
from ..services import NotificationService, StockSynchronizer


@dataclass(frozen=True)
class TriggerStocksNotificationsRequest:
    symbols: list[str]
    targets: dict[str, list[Decimal]] = field(default_factory=dict)


class TriggerStocksNotifications:
    def __init__(
        self,
        stock_synchronizer: StockSynchronizer,
        notification_service: NotificationService,
    ) -> None:
        self._stock_synchronizer = stock_synchronizer
        self._notification_service = notification_service

    def handle(self, request: TriggerStocksNotificationsRequest) -> list[TargetPriceDTO]:
        stocks = self._stock_synchronizer.fetch_and_sync(request.symbols, request.targets)

        fulfilled: list[TargetPriceDTO] = []
        for stock in stocks:
            self._notification_service.send_stock_notifications(stock)
            for target_value in stock.drain_fulfilled_targets():
                fulfilled.append(TargetPriceDTO(symbol=stock.symbol, target=target_value))

        self._stock_synchronizer.persist(stocks)
        return fulfilled

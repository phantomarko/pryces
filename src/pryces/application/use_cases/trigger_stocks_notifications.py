from dataclasses import dataclass
from enum import Enum

from ..dtos import StockDTO
from ..interfaces import MessageSender, StockProvider


class TriggerType(str, Enum):
    MILESTONES = "MILESTONES"


@dataclass(frozen=True)
class TriggerStocksNotificationsRequest:
    type: TriggerType
    symbols: list[str]


class TriggerStocksNotifications:
    def __init__(self, provider: StockProvider, sender: MessageSender) -> None:
        self._provider = provider
        self._sender = sender

    def handle(self, request: TriggerStocksNotificationsRequest) -> list[StockDTO]:
        stocks = self._provider.get_stocks(request.symbols)

        if request.type == TriggerType.MILESTONES:
            for stock in stocks:
                stock.generate_milestones_notifications()
                for notification in stock.notifications:
                    self._sender.send_message(notification.message)

        return [StockDTO.from_stock(stock) for stock in stocks]

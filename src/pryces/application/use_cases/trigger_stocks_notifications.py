from dataclasses import dataclass, field
from decimal import Decimal

from pryces.domain.stocks import Stock
from pryces.domain.target_prices import TargetPrice
from ..dtos import TargetPriceDTO
from ..providers import StockProvider
from ..repositories import StockRepository
from ..services import NotificationService


@dataclass(frozen=True)
class TriggerStocksNotificationsRequest:
    symbols: list[str]
    targets: dict[str, list[Decimal]] = field(default_factory=dict)


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

    def handle(self, request: TriggerStocksNotificationsRequest) -> list[TargetPriceDTO]:
        fresh_stocks = self._provider.get_stocks(request.symbols)
        fulfilled: list[TargetPriceDTO] = []
        stocks_to_save: list[Stock] = []

        for fresh_stock in fresh_stocks:
            existing = self._stock_repository.get(fresh_stock.symbol)
            if existing is not None:
                existing.update(fresh_stock)
                stock = existing
            else:
                stock = fresh_stock

            target_values = request.targets.get(stock.symbol, [])
            stock.sync_targets([TargetPrice(stock.symbol, v) for v in target_values])

            targets_before = [t.target for t in stock.targets]
            self._notification_service.send_stock_notifications(stock)
            targets_after = {t.target for t in stock.targets}

            for target_value in targets_before:
                if target_value not in targets_after:
                    fulfilled.append(TargetPriceDTO(symbol=stock.symbol, target=target_value))

            stocks_to_save.append(stock)

        self._stock_repository.save_batch(stocks_to_save)
        return fulfilled

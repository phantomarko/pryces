from dataclasses import dataclass

from pryces.domain.stocks import Stock
from pryces.domain.target_prices import TargetPrice
from ..dtos import TargetPriceDTO
from ..providers import StockProvider
from ..repositories import StockRepository, TargetPriceRepository
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
        target_price_repository: TargetPriceRepository,
    ) -> None:
        self._provider = provider
        self._notification_service = notification_service
        self._stock_repository = stock_repository
        self._target_price_repository = target_price_repository

    def handle(self, request: TriggerStocksNotificationsRequest) -> list[TargetPriceDTO]:
        fresh_stocks = self._provider.get_stocks(request.symbols)
        fulfilled: list[TargetPrice] = []
        stocks_to_save: list[Stock] = []

        for fresh_stock in fresh_stocks:
            existing = self._stock_repository.get(fresh_stock.symbol)
            if existing is not None:
                existing.update(fresh_stock)
                stock = existing
            else:
                stock = fresh_stock
            stocks_to_save.append(stock)

            targets = self._target_price_repository.get_by_symbol([stock.symbol])
            self._set_entry_prices(stock, targets)
            triggered = self._notification_service.send_stock_notifications(stock, targets)
            for target in triggered:
                self._target_price_repository.delete(target)
            fulfilled.extend(triggered)

        self._stock_repository.save_batch(stocks_to_save)
        return [TargetPriceDTO.from_target_price(t) for t in fulfilled]

    def _set_entry_prices(self, stock: Stock, targets: list[TargetPrice]) -> None:
        for target in targets:
            is_new_entry = target.entry is None
            target.set_entry_price(stock)
            if is_new_entry:
                self._target_price_repository.save(target)

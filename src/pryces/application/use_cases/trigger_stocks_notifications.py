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
        stocks = self._provider.get_stocks(request.symbols)
        fulfilled: list[TargetPrice] = []

        for stock in stocks:
            past_stock = self._stock_repository.get(stock.symbol)
            targets = self._target_price_repository.get_by_symbol([stock.symbol])
            self._set_entry_prices(stock, targets)
            self._notification_service.send_stock_notifications(stock, past_stock)
            triggered = self._notification_service.send_stock_targets_notifications(stock, targets)
            for target in triggered:
                self._target_price_repository.delete(target)
            fulfilled.extend(triggered)

        self._stock_repository.save_batch(stocks)
        return [TargetPriceDTO.from_target_price(t) for t in fulfilled]

    def _set_entry_prices(self, stock: Stock, targets: list[TargetPrice]) -> None:
        for target in targets:
            is_new_entry = target.entry is None
            target.set_entry_price(stock)
            if is_new_entry:
                self._target_price_repository.save(target)

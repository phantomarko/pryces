from dataclasses import dataclass

from ..interfaces import StockPriceProvider, StockPrice


@dataclass(frozen=True)
class GetStocksPricesRequest:
    symbols: list[str]


class GetStocksPrices:
    def __init__(self, provider: StockPriceProvider) -> None:
        self._provider = provider

    def handle(self, request: GetStocksPricesRequest) -> list[StockPrice]:
        return self._provider.get_stocks_prices(request.symbols)

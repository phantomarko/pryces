from dataclasses import dataclass

from ..dtos import StockPriceDTO
from ..interfaces import StockPriceProvider


@dataclass(frozen=True)
class GetStocksPricesRequest:
    symbols: list[str]


class GetStocksPrices:
    def __init__(self, provider: StockPriceProvider) -> None:
        self._provider = provider

    def handle(self, request: GetStocksPricesRequest) -> list[StockPriceDTO]:
        responses = self._provider.get_stocks_prices(request.symbols)
        return [StockPriceDTO.from_stock_price(response) for response in responses]

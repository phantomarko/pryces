from dataclasses import dataclass

from ..dtos import StockPriceDTO
from ..interfaces import StockProvider


@dataclass(frozen=True)
class GetStocksPricesRequest:
    symbols: list[str]


class GetStocksPrices:
    def __init__(self, provider: StockProvider) -> None:
        self._provider = provider

    def handle(self, request: GetStocksPricesRequest) -> list[StockPriceDTO]:
        responses = self._provider.get_stocks(request.symbols)
        return [StockPriceDTO.from_stock(response) for response in responses]

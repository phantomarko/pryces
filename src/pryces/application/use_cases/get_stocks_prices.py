from dataclasses import dataclass

from ..dtos import StockDTO
from ..interfaces import StockProvider


@dataclass(frozen=True)
class GetStocksPricesRequest:
    symbols: list[str]


class GetStocksPrices:
    def __init__(self, provider: StockProvider) -> None:
        self._provider = provider

    def handle(self, request: GetStocksPricesRequest) -> list[StockDTO]:
        responses = self._provider.get_stocks(request.symbols)
        return [StockDTO.from_stock(response) for response in responses]

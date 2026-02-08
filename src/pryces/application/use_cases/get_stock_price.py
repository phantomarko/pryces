from dataclasses import dataclass

from ..dtos import StockDTO
from ..exceptions import StockNotFound
from ..interfaces import StockProvider


@dataclass(frozen=True)
class GetStockPriceRequest:
    symbol: str


class GetStockPrice:
    def __init__(self, provider: StockProvider) -> None:
        self._provider = provider

    def handle(self, request: GetStockPriceRequest) -> StockDTO:
        response = self._provider.get_stock(request.symbol)

        if response is None:
            raise StockNotFound(request.symbol)

        return StockDTO.from_stock(response)

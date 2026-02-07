from dataclasses import dataclass

from ..dtos import StockPriceDTO
from ..exceptions import StockNotFound
from ..interfaces import StockPriceProvider


@dataclass(frozen=True)
class GetStockPriceRequest:
    symbol: str


class GetStockPrice:
    def __init__(self, provider: StockPriceProvider) -> None:
        self._provider = provider

    def handle(self, request: GetStockPriceRequest) -> StockPriceDTO:
        response = self._provider.get_stock_price(request.symbol)

        if response is None:
            raise StockNotFound(request.symbol)

        return StockPriceDTO.from_stock(response)

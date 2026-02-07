from dataclasses import dataclass

from ..exceptions import StockNotFound
from ..interfaces import StockPriceProvider, StockPrice


@dataclass(frozen=True)
class GetStockPriceRequest:
    symbol: str


class GetStockPrice:
    def __init__(self, provider: StockPriceProvider) -> None:
        self._provider = provider

    def handle(self, request: GetStockPriceRequest) -> StockPrice:
        response = self._provider.get_stock_price(request.symbol)

        if response is None:
            raise StockNotFound(request.symbol)

        return response

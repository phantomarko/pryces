from ..application.interfaces import StockRepository
from ..domain.stocks import Stock


class InMemoryStockRepository(StockRepository):
    def __init__(self) -> None:
        self._store: dict[str, Stock] = {}

    def save_batch(self, stocks: list[Stock]) -> None:
        for stock in stocks:
            self._store[stock.symbol] = stock

    def get(self, symbol: str) -> Stock | None:
        return self._store.get(symbol)

from datetime import datetime

from ..application.repositories import (
    MarketTransitionRepository,
    StockRepository,
)
from ..domain.stocks import Stock


class InMemoryStockRepository(StockRepository):
    def __init__(self) -> None:
        self._store: dict[str, Stock] = {}

    def save_batch(self, stocks: list[Stock]) -> None:
        for stock in stocks:
            self._store[stock.symbol] = stock

    def get(self, symbol: str) -> Stock | None:
        return self._store.get(symbol)


class InMemoryMarketTransitionRepository(MarketTransitionRepository):
    def __init__(self) -> None:
        self._store: dict[str, datetime] = {}

    def save(self, symbol: str, transition_time: datetime) -> None:
        self._store[symbol] = transition_time

    def get(self, symbol: str) -> datetime | None:
        return self._store.get(symbol)

    def delete(self, symbol: str) -> None:
        self._store.pop(symbol, None)

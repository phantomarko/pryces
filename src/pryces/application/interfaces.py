from abc import ABC, abstractmethod
from datetime import datetime

from pryces.domain.stocks import Stock


class StockProvider(ABC):
    @abstractmethod
    def get_stock(self, symbol: str) -> Stock | None:
        pass

    @abstractmethod
    def get_stocks(self, symbols: list[str]) -> list[Stock]:
        pass


class StockRepository(ABC):
    @abstractmethod
    def save_batch(self, stocks: list[Stock]) -> None:
        pass

    @abstractmethod
    def get(self, symbol: str) -> Stock | None:
        pass


class MarketTransitionRepository(ABC):
    @abstractmethod
    def save(self, symbol: str, transition_time: datetime) -> None:
        pass

    @abstractmethod
    def get(self, symbol: str) -> datetime | None:
        pass

    @abstractmethod
    def delete(self, symbol: str) -> None:
        pass


class MessageSender(ABC):
    @abstractmethod
    def send_message(self, message: str) -> bool:
        pass

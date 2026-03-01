from abc import ABC, abstractmethod
from datetime import datetime

from pryces.domain.target_prices import TargetPrice
from pryces.domain.stocks import Stock


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


class TargetPriceRepository(ABC):
    @abstractmethod
    def get_by_symbol(self, symbols: list[str]) -> list[TargetPrice]:
        pass

    @abstractmethod
    def save(self, price_target: TargetPrice) -> None:
        pass

    @abstractmethod
    def delete(self, price_target: TargetPrice) -> None:
        pass

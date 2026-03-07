from abc import ABC, abstractmethod
from datetime import datetime

from pryces.domain.stocks import Stock


class StockProvider(ABC):
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
        # Returns True when accepted for delivery — not necessarily delivered yet.
        pass


class Logger(ABC):
    @abstractmethod
    def debug(self, message: str) -> None:
        pass

    @abstractmethod
    def info(self, message: str) -> None:
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        pass


class LoggerFactory(ABC):
    @abstractmethod
    def get_logger(self, name: str) -> Logger:
        pass

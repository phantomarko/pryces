from abc import ABC, abstractmethod

from pryces.domain.stock_statistics import StockStatistics
from pryces.domain.stocks import Stock


class StockProvider(ABC):
    @abstractmethod
    def get_stocks(self, symbols: list[str]) -> list[Stock]:
        pass


class StockStatisticsProvider(ABC):
    @abstractmethod
    def get_stock_statistics(self, symbols: list[str]) -> list[StockStatistics]:
        pass


class StockRepository(ABC):
    @abstractmethod
    def save_batch(self, stocks: list[Stock]) -> None:
        pass

    @abstractmethod
    def get(self, symbol: str) -> Stock | None:
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

from abc import ABC, abstractmethod

from pryces.domain.stocks import Stock


class StockPriceProvider(ABC):
    @abstractmethod
    def get_stock_price(self, symbol: str) -> Stock | None:
        pass

    @abstractmethod
    def get_stocks_prices(self, symbols: list[str]) -> list[Stock]:
        pass


class MessageSender(ABC):
    @abstractmethod
    def send_message(self, message: str) -> bool:
        pass

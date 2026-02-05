from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class StockPriceResponse:
    symbol: str
    currentPrice: Decimal
    name: str | None = None
    currency: str | None = None
    previousClosePrice: Decimal | None = None
    openPrice: Decimal | None = None
    dayHigh: Decimal | None = None
    dayLow: Decimal | None = None
    fiftyDayAverage: Decimal | None = None
    twoHundredDayAverage: Decimal | None = None
    fiftyTwoWeekHigh: Decimal | None = None
    fiftyTwoWeekLow: Decimal | None = None


class StockPriceProvider(ABC):
    @abstractmethod
    def get_stock_price(self, symbol: str) -> StockPriceResponse | None:
        pass

    @abstractmethod
    def get_stocks_prices(self, symbols: list[str]) -> list[StockPriceResponse]:
        pass

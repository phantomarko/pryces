"""Provider interfaces and data transfer objects.

This module defines the interfaces for external service providers and their
associated DTOs, following the dependency inversion principle of clean architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class StockPriceResponse:
    """Response DTO for stock price queries."""
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
    """Interface for retrieving stock price information.

    Implementations of this interface will be provided in the infrastructure layer.
    """

    @abstractmethod
    def get_stock_price(self, symbol: str) -> StockPriceResponse | None:
        """Retrieve current price for a given stock symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

        Returns:
            StockPriceResponse with required fields (symbol, currentPrice) and optional
            fields, or None if symbol not found

        Raises:
            StockInformationIncomplete: When symbol is found but current price unavailable
            Exception: Implementation-specific exceptions for failures
        """
        pass

    @abstractmethod
    def get_stocks_prices(self, symbols: list[str]) -> list[StockPriceResponse]:
        """Retrieve current prices for multiple stock symbols.

        Args:
            symbols: List of stock ticker symbols (e.g., ['AAPL', 'GOOGL', 'TSLA'])

        Returns:
            List of StockPriceResponse for successfully retrieved symbols only.
            Failed symbols (not found or incomplete data) are omitted from results.
            Result length may be less than input length.

        Notes:
            - Empty list returns empty list
            - Failed symbols are silently skipped (not included in results)
            - No None values in returned list
        """
        pass

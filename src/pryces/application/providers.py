"""Provider interfaces and data transfer objects.

This module defines the interfaces for external service providers and their
associated DTOs, following the dependency inversion principle of clean architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class StockPriceResponse:
    """Response DTO for stock price queries.

    Attributes:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        price: Current stock price as a Decimal for precision
        currency: Currency code (e.g., 'USD', 'EUR')
    """
    ticker: str
    price: Decimal
    currency: str


class StockPriceProvider(ABC):
    """Interface for retrieving stock price information.

    Implementations of this interface will be provided in the infrastructure layer.
    """

    @abstractmethod
    def get_stock_price(self, ticker: str) -> StockPriceResponse | None:
        """Retrieve current price for a given stock ticker.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

        Returns:
            StockPriceResponse containing ticker, price, and currency, or None if not found

        Raises:
            Exception: Implementation-specific exceptions for failures
        """
        pass

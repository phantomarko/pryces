"""Interfaces for external service providers."""

from abc import ABC, abstractmethod

from .dtos import StockPriceResponse


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

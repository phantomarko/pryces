"""Get stock price use case implementation.

This module contains the use case for retrieving stock price information,
including the request DTO and the use case orchestrator.
"""

from dataclasses import dataclass

from ..exceptions import StockNotFound
from ..providers import StockPriceProvider, StockPriceResponse


@dataclass(frozen=True)
class GetStockPriceRequest:
    """Request DTO for getting stock price.

    Attributes:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
    """
    ticker: str


class GetStockPrice:
    """Use case for retrieving stock price information.

    This use case orchestrates the retrieval of stock prices by delegating
    to a stock price provider implementation.
    """

    def __init__(self, provider: StockPriceProvider) -> None:
        """Initialize the use case with a stock price provider.

        Args:
            provider: Implementation of StockPriceProvider interface
        """
        self._provider = provider

    def handle(self, request: GetStockPriceRequest) -> StockPriceResponse:
        """Handle a stock price request.

        Args:
            request: GetStockPriceRequest containing the ticker symbol

        Returns:
            StockPriceResponse containing ticker, price, and currency

        Raises:
            StockNotFound: If the stock ticker is not found
            Exception: Provider-specific exceptions for failures
        """
        response = self._provider.get_stock_price(request.ticker)

        if response is None:
            raise StockNotFound(request.ticker)

        return response

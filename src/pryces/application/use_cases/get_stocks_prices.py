"""Use case for retrieving prices for multiple stock symbols."""

from dataclasses import dataclass

from ..providers import StockPriceProvider, StockPriceResponse


@dataclass(frozen=True)
class GetStocksPricesRequest:
    """Request DTO for getting multiple stock prices.

    Attributes:
        symbols: List of stock ticker symbols (e.g., ['AAPL', 'GOOGL'])
    """
    symbols: list[str]


class GetStocksPrices:
    """Use case for retrieving multiple stock prices in batch."""

    def __init__(self, provider: StockPriceProvider) -> None:
        self._provider = provider

    def handle(self, request: GetStocksPricesRequest) -> list[StockPriceResponse]:
        """Handle a batch stock price request.

        Args:
            request: GetStocksPricesRequest containing list of symbols

        Returns:
            List of StockPriceResponse for successfully retrieved symbols only.
            Failed symbols (not found or incomplete data) are silently skipped.

        Notes:
            - Empty input returns empty list
            - Result may contain fewer items than requested symbols
            - Duplicate symbols may result in duplicate responses
        """
        return self._provider.get_stocks_prices(request.symbols)

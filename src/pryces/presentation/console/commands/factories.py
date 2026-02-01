"""Factories for creating console command instances.

This module provides factory classes for creating command instances with
their required dependencies properly wired up.
"""

from decimal import Decimal

from ....application.providers.dtos import StockPriceResponse
from ....application.providers.interfaces import StockPriceProvider
from ....application.use_cases.get_stock_price.get_stock_price import GetStockPrice
from .get_stock_price import GetStockPriceCommand


class MockStockPriceProvider(StockPriceProvider):
    """Mock stock price provider for demonstration purposes.

    This is a temporary implementation for testing and demonstration.
    Replace with a real provider implementation (e.g., YahooFinanceProvider,
    AlphaVantageProvider) in production.
    """

    def get_stock_price(self, ticker: str) -> StockPriceResponse | None:
        """Return mock stock price data.

        Args:
            ticker: Stock ticker symbol

        Returns:
            StockPriceResponse with mock data if ticker exists, None otherwise
        """
        mock_prices = {
            "AAPL": Decimal("150.25"),
            "GOOGL": Decimal("2847.50"),
            "TSLA": Decimal("200.00"),
            "MSFT": Decimal("350.75"),
        }

        if ticker.upper() in mock_prices:
            return StockPriceResponse(
                ticker=ticker.upper(),
                price=mock_prices[ticker.upper()],
                currency="USD"
            )
        return None


class CommandFactory:
    """Factory for creating console command instances.

    This factory handles the creation and wiring of command instances with
    their dependencies. It serves as a simple dependency injection container
    for the console layer.
    """

    def __init__(self, stock_price_provider: StockPriceProvider | None = None) -> None:
        """Initialize the command factory.

        Args:
            stock_price_provider: Optional stock price provider.
                If not provided, uses MockStockPriceProvider.
        """
        self._stock_price_provider = stock_price_provider or MockStockPriceProvider()

    def create_get_stock_price_command(self) -> GetStockPriceCommand:
        """Create and configure a GetStockPriceCommand instance.

        Returns:
            Configured GetStockPriceCommand with all dependencies wired up
        """
        use_case = GetStockPrice(provider=self._stock_price_provider)
        return GetStockPriceCommand(get_stock_price_use_case=use_case)

"""Factories for creating console command instances.

This module provides factory classes for creating command instances with
their required dependencies properly wired up.
"""

from ....application.providers import StockPriceProvider
from ....application.use_cases.get_stock_price import GetStockPrice
from ....application.use_cases.get_stocks_prices import GetStocksPrices
from ....infrastructure.providers import YahooFinanceProvider
from .get_stock_price import GetStockPriceCommand
from .get_stocks_prices import GetStocksPricesCommand
from .registry import CommandRegistry


class CommandFactory:
    """Factory for creating console command instances with their dependencies."""

    def __init__(self, stock_price_provider: StockPriceProvider) -> None:
        self._stock_price_provider = stock_price_provider

    def create_get_stock_price_command(self) -> GetStockPriceCommand:
        use_case = GetStockPrice(provider=self._stock_price_provider)
        return GetStockPriceCommand(get_stock_price_use_case=use_case)

    def create_get_stocks_prices_command(self) -> GetStocksPricesCommand:
        use_case = GetStocksPrices(provider=self._stock_price_provider)
        return GetStocksPricesCommand(get_stocks_prices_use_case=use_case)

    def create_command_registry(self) -> CommandRegistry:
        registry = CommandRegistry()
        registry.register(self.create_get_stock_price_command())
        registry.register(self.create_get_stocks_prices_command())
        return registry

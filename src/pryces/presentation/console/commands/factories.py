"""Factories for creating console command instances.

This module provides factory classes for creating command instances with
their required dependencies properly wired up.
"""

from ....application.providers import StockPriceProvider
from ....application.use_cases.get_stock_price import GetStockPrice
from ....infrastructure.providers import YahooFinanceProvider
from .get_stock_price import GetStockPriceCommand
from .registry import CommandRegistry


class CommandFactory:
    """Factory for creating console command instances with their dependencies."""

    def __init__(self, stock_price_provider: StockPriceProvider) -> None:
        """Initialize the command factory."""
        self._stock_price_provider = stock_price_provider

    def create_get_stock_price_command(self) -> GetStockPriceCommand:
        """Create and configure a GetStockPriceCommand instance.

        Returns:
            Configured GetStockPriceCommand with all dependencies wired up
        """
        use_case = GetStockPrice(provider=self._stock_price_provider)
        return GetStockPriceCommand(get_stock_price_use_case=use_case)

    def create_command_registry(self) -> CommandRegistry:
        """Create a CommandRegistry with all available commands.

        Returns:
            CommandRegistry with all commands registered
        """
        registry = CommandRegistry()
        registry.register(self.create_get_stock_price_command())
        return registry

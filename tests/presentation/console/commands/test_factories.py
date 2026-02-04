"""Unit tests for CommandFactory."""

from decimal import Decimal
from unittest.mock import Mock

from pryces.application.providers import StockPriceProvider, StockPriceResponse
from pryces.presentation.console.commands.factories import CommandFactory
from pryces.presentation.console.commands.get_stock_price import GetStockPriceCommand
from pryces.presentation.console.commands.get_stocks_prices import GetStocksPricesCommand
from pryces.presentation.console.commands.registry import CommandRegistry
from tests.fixtures.factories import create_stock_price


class TestCommandFactory:
    """Test suite for CommandFactory."""

    def test_init_accepts_custom_provider(self):
        """Test that factory accepts a custom provider."""
        # Arrange
        custom_provider = Mock(spec=StockPriceProvider)

        # Act
        factory = CommandFactory(stock_price_provider=custom_provider)

        # Assert
        assert factory._stock_price_provider is custom_provider

    def test_create_get_stock_price_command_returns_command_instance(self):
        """Test that factory creates GetStockPriceCommand instance."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        command = factory.create_get_stock_price_command()

        # Assert
        assert isinstance(command, GetStockPriceCommand)

    def test_create_get_stock_price_command_wires_dependencies_correctly(self):
        """Test that created command works with mocked provider."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stock_price.return_value = StockPriceResponse(
            symbol="TEST",
            name="Test Company",
            currentPrice=Decimal("100.00"),
            currency="USD",
            previousClosePrice=Decimal("99.00"),
            openPrice=Decimal("99.50"),
            dayHigh=Decimal("101.00"),
            dayLow=Decimal("98.00"),
            fiftyDayAverage=Decimal("100.00"),
            twoHundredDayAverage=Decimal("100.00"),
            fiftyTwoWeekHigh=Decimal("120.00"),
            fiftyTwoWeekLow=Decimal("80.00")
        )
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        command = factory.create_get_stock_price_command()
        result = command.execute("TEST")

        # Assert
        assert "TEST" in result
        assert "100.00" in result
        mock_provider.get_stock_price.assert_called_once()

    def test_create_get_stock_price_command_with_default_provider(self):
        """Test that command works with injected provider."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stock_price.return_value = create_stock_price(
            "AAPL",
            Decimal("150.25"),
            name="Apple Inc."
        )
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        command = factory.create_get_stock_price_command()
        result = command.execute("AAPL")

        # Assert
        assert '"success": true' in result
        assert "AAPL" in result
        assert "150.25" in result

    def test_create_command_registry_returns_registry_instance(self):
        """Test that factory creates CommandRegistry instance."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        registry = factory.create_command_registry()

        # Assert
        assert isinstance(registry, CommandRegistry)

    def test_registry_contains_get_stock_price_command(self):
        """Test that registry contains GetStockPrice command."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        registry = factory.create_command_registry()
        all_commands = registry.get_all_commands()

        # Assert
        assert len(all_commands) > 0
        command = registry.get_command("get_stock_price")
        assert isinstance(command, GetStockPriceCommand)

    def test_registry_commands_are_functional(self):
        """Test that commands in registry are properly wired and functional."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stock_price.return_value = create_stock_price(
            "AAPL",
            Decimal("150.25"),
            name="Apple Inc."
        )
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        registry = factory.create_command_registry()
        command = registry.get_command("get_stock_price")
        result = command.execute(symbol="AAPL")

        # Assert
        assert '"success": true' in result
        assert "AAPL" in result

    def test_create_get_stocks_prices_command_returns_command_instance(self):
        """Test that factory creates GetStocksPricesCommand instance."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        command = factory.create_get_stocks_prices_command()

        # Assert
        assert isinstance(command, GetStocksPricesCommand)

    def test_create_get_stocks_prices_command_wires_dependencies_correctly(self):
        """Test that created command works with mocked provider."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stocks_prices.return_value = [
            StockPriceResponse(
                symbol="AAPL",
                name="Apple Inc.",
                currentPrice=Decimal("150.25"),
                currency="USD"
            ),
            StockPriceResponse(
                symbol="GOOGL",
                name="Alphabet Inc.",
                currentPrice=Decimal("2847.50"),
                currency="USD"
            )
        ]
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        command = factory.create_get_stocks_prices_command()
        result = command.execute("AAPL,GOOGL")

        # Assert
        assert "AAPL" in result
        assert "GOOGL" in result
        assert "150.25" in result
        assert "2847.50" in result
        mock_provider.get_stocks_prices.assert_called_once()

    def test_registry_contains_get_stocks_prices_command(self):
        """Test that registry contains GetStocksPrices command."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        registry = factory.create_command_registry()
        command = registry.get_command("get_stocks_prices")

        # Assert
        assert isinstance(command, GetStocksPricesCommand)

    def test_registry_get_stocks_prices_command_is_functional(self):
        """Test that GetStocksPrices command in registry is properly wired."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stocks_prices.return_value = [
            create_stock_price("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock_price("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
            create_stock_price("MSFT", Decimal("350.75"), name="Microsoft Corporation"),
        ]
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        registry = factory.create_command_registry()
        command = registry.get_command("get_stocks_prices")
        result = command.execute(symbols="AAPL,GOOGL,MSFT")

        # Assert
        assert '"success": true' in result
        assert "AAPL" in result
        assert "GOOGL" in result
        assert "MSFT" in result

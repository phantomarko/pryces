"""Unit tests for CommandFactory."""

from decimal import Decimal
from unittest.mock import Mock

from pryces.application.providers import StockPriceProvider, StockPriceResponse
from pryces.presentation.console.commands.factories import CommandFactory
from pryces.presentation.console.commands.get_stock_price import GetStockPriceCommand
from tests.fixtures import MockStockPriceProvider


class TestMockStockPriceProvider:
    """Test suite for MockStockPriceProvider."""

    def setup_method(self):
        self.provider = MockStockPriceProvider()

    def test_get_stock_price_returns_response_for_valid_symbol(self):
        """Test that provider returns response for known symbols."""
        # Arrange
        symbol = "AAPL"

        # Act
        result = self.provider.get_stock_price(symbol)

        # Assert
        assert result is not None
        assert result.symbol == "AAPL"
        assert result.currentPrice == Decimal("150.25")
        assert result.name == "Apple Inc."
        assert result.currency == "USD"

    def test_get_stock_price_handles_case_insensitive_symbol(self):
        """Test that provider handles lowercase symbols."""
        # Arrange
        symbol = "aapl"

        # Act
        result = self.provider.get_stock_price(symbol)

        # Assert
        assert result is not None
        assert result.symbol == "AAPL"

    def test_get_stock_price_returns_none_for_unknown_symbol(self):
        """Test that provider returns None for unknown symbols."""
        # Arrange
        symbol = "UNKNOWN"

        # Act
        result = self.provider.get_stock_price(symbol)

        # Assert
        assert result is None

    def test_get_stock_price_returns_different_prices_for_different_symbols(self):
        """Test that provider returns correct prices for different symbols."""
        # Act
        aapl = self.provider.get_stock_price("AAPL")
        googl = self.provider.get_stock_price("GOOGL")

        # Assert
        assert aapl.currentPrice == Decimal("150.25")
        assert googl.currentPrice == Decimal("2847.50")


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
        mock_provider = MockStockPriceProvider()
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
        """Test that command works with injected MockStockPriceProvider."""
        # Arrange
        mock_provider = MockStockPriceProvider()
        factory = CommandFactory(stock_price_provider=mock_provider)

        # Act
        command = factory.create_get_stock_price_command()
        result = command.execute("AAPL")

        # Assert
        assert '"success": true' in result
        assert "AAPL" in result
        assert "150.25" in result

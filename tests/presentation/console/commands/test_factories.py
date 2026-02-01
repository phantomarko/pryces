"""Unit tests for CommandFactory."""

from decimal import Decimal
from unittest.mock import Mock

from pryces.application.providers import StockPriceProvider, StockPriceResponse
from pryces.presentation.console.commands.factories import (
    CommandFactory,
    MockStockPriceProvider,
)
from pryces.presentation.console.commands.get_stock_price import (
    GetStockPriceCommand,
)


class TestMockStockPriceProvider:
    """Test suite for MockStockPriceProvider."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.provider = MockStockPriceProvider()

    def test_get_stock_price_returns_response_for_valid_ticker(self):
        """Test that provider returns response for known tickers."""
        # Arrange
        ticker = "AAPL"

        # Act
        result = self.provider.get_stock_price(ticker)

        # Assert
        assert result is not None
        assert result.ticker == "AAPL"
        assert result.price == Decimal("150.25")
        assert result.currency == "USD"

    def test_get_stock_price_handles_case_insensitive_ticker(self):
        """Test that provider handles lowercase tickers."""
        # Arrange
        ticker = "aapl"

        # Act
        result = self.provider.get_stock_price(ticker)

        # Assert
        assert result is not None
        assert result.ticker == "AAPL"

    def test_get_stock_price_returns_none_for_unknown_ticker(self):
        """Test that provider returns None for unknown tickers."""
        # Arrange
        ticker = "UNKNOWN"

        # Act
        result = self.provider.get_stock_price(ticker)

        # Assert
        assert result is None

    def test_get_stock_price_returns_different_prices_for_different_tickers(self):
        """Test that provider returns correct prices for different tickers."""
        # Act
        aapl = self.provider.get_stock_price("AAPL")
        googl = self.provider.get_stock_price("GOOGL")

        # Assert
        assert aapl.price == Decimal("150.25")
        assert googl.price == Decimal("2847.50")


class TestCommandFactory:
    """Test suite for CommandFactory."""

    def test_init_uses_mock_provider_by_default(self):
        """Test that factory uses MockStockPriceProvider when no provider given."""
        # Act
        factory = CommandFactory()

        # Assert
        assert isinstance(factory._stock_price_provider, MockStockPriceProvider)

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
        factory = CommandFactory()

        # Act
        command = factory.create_get_stock_price_command()

        # Assert
        assert isinstance(command, GetStockPriceCommand)

    def test_create_get_stock_price_command_wires_dependencies_correctly(self):
        """Test that created command works with mocked provider."""
        # Arrange
        mock_provider = Mock(spec=StockPriceProvider)
        mock_provider.get_stock_price.return_value = StockPriceResponse(
            ticker="TEST",
            price=Decimal("100.00"),
            currency="USD"
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
        """Test that command works with default MockStockPriceProvider."""
        # Arrange
        factory = CommandFactory()

        # Act
        command = factory.create_get_stock_price_command()
        result = command.execute("AAPL")

        # Assert
        assert '"success": true' in result
        assert "AAPL" in result
        assert "150.25" in result

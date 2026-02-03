"""Tests for GetStocksPrices use case."""

from decimal import Decimal
from unittest.mock import Mock
import pytest

from pryces.application.use_cases.get_stocks_prices import (
    GetStocksPrices,
    GetStocksPricesRequest,
)
from pryces.application.providers import StockPriceProvider, StockPriceResponse


class TestGetStocksPrices:
    """Test suite for GetStocksPrices use case."""

    def setup_method(self):
        self.mock_provider = Mock(spec=StockPriceProvider)

    def test_handle_returns_all_successful_results(self):
        """All symbols found - returns complete list."""
        # Arrange
        responses = [
            StockPriceResponse(symbol="AAPL", currentPrice=Decimal("150.25")),
            StockPriceResponse(symbol="GOOGL", currentPrice=Decimal("2847.50")),
            StockPriceResponse(symbol="MSFT", currentPrice=Decimal("350.75"))
        ]
        self.mock_provider.get_stocks_prices.return_value = responses
        request = GetStocksPricesRequest(symbols=["AAPL", "GOOGL", "MSFT"])
        use_case = GetStocksPrices(provider=self.mock_provider)

        # Act
        result = use_case.handle(request)

        # Assert
        assert len(result) == 3
        assert result == responses
        self.mock_provider.get_stocks_prices.assert_called_once_with(["AAPL", "GOOGL", "MSFT"])

    def test_handle_filters_out_not_found_symbols(self):
        """Mixed results - provider returns only successful responses."""
        # Provider already filtered out None values
        responses = [
            StockPriceResponse(symbol="AAPL", currentPrice=Decimal("150.25")),
            StockPriceResponse(symbol="MSFT", currentPrice=Decimal("350.75"))
        ]
        self.mock_provider.get_stocks_prices.return_value = responses
        request = GetStocksPricesRequest(symbols=["AAPL", "INVALID", "MSFT"])
        use_case = GetStocksPrices(provider=self.mock_provider)

        # Act
        result = use_case.handle(request)

        # Assert
        assert len(result) == 2
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "MSFT"

    def test_handle_returns_empty_list_when_all_symbols_not_found(self):
        """No symbols found - provider returns empty list."""
        self.mock_provider.get_stocks_prices.return_value = []
        request = GetStocksPricesRequest(symbols=["INVALID1", "INVALID2", "INVALID3"])
        use_case = GetStocksPrices(provider=self.mock_provider)

        # Act
        result = use_case.handle(request)

        # Assert
        assert len(result) == 0
        assert result == []

    def test_handle_returns_empty_list_for_empty_input(self):
        """Empty input - returns empty list."""
        self.mock_provider.get_stocks_prices.return_value = []
        request = GetStocksPricesRequest(symbols=[])
        use_case = GetStocksPrices(provider=self.mock_provider)

        # Act
        result = use_case.handle(request)

        # Assert
        assert len(result) == 0
        self.mock_provider.get_stocks_prices.assert_called_once_with([])

    def test_handle_processes_duplicate_symbols(self):
        """Duplicate symbols are processed independently."""
        responses = [
            StockPriceResponse(symbol="AAPL", currentPrice=Decimal("150.25")),
            StockPriceResponse(symbol="AAPL", currentPrice=Decimal("150.25"))
        ]
        self.mock_provider.get_stocks_prices.return_value = responses
        request = GetStocksPricesRequest(symbols=["AAPL", "AAPL"])
        use_case = GetStocksPrices(provider=self.mock_provider)

        # Act
        result = use_case.handle(request)

        # Assert
        assert len(result) == 2
        assert all(r.symbol == "AAPL" for r in result)

    def test_handle_with_responses_containing_minimal_fields(self):
        """Responses with only required fields work correctly."""
        responses = [
            StockPriceResponse(symbol="AAPL", currentPrice=Decimal("150.25")),
            StockPriceResponse(symbol="GOOGL", currentPrice=Decimal("2847.50"))
        ]
        self.mock_provider.get_stocks_prices.return_value = responses
        request = GetStocksPricesRequest(symbols=["AAPL", "GOOGL"])
        use_case = GetStocksPrices(provider=self.mock_provider)

        # Act
        result = use_case.handle(request)

        # Assert
        assert len(result) == 2
        assert result[0].name is None
        assert result[0].currency is None

"""Unit tests for GetStockPriceCommand."""

import json
from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.application.providers.dtos import StockPriceResponse
from pryces.application.use_cases.get_stock_price import (
    GetStockPrice,
    StockNotFound,
)
from pryces.presentation.console.commands.get_stock_price import (
    GetStockPriceCommand,
)


class TestGetStockPriceCommand:
    """Test suite for GetStockPriceCommand."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_use_case = Mock(spec=GetStockPrice)
        self.command = GetStockPriceCommand(self.mock_use_case)

    def test_execute_returns_success_json_with_stock_data(self):
        """Test that execute() returns success JSON when stock is found."""
        # Arrange
        ticker = "AAPL"
        stock_response = StockPriceResponse(
            ticker=ticker,
            price=Decimal("150.25"),
            currency="USD"
        )
        self.mock_use_case.handle.return_value = stock_response

        # Act
        result = self.command.execute(ticker)

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"]["ticker"] == ticker
        assert result_data["data"]["price"] == "150.25"
        assert result_data["data"]["currency"] == "USD"

    def test_execute_handles_decimal_precision_in_json(self):
        """Test that execute() preserves Decimal precision in JSON output."""
        # Arrange
        ticker = "GOOGL"
        stock_response = StockPriceResponse(
            ticker=ticker,
            price=Decimal("2847.123456789"),
            currency="USD"
        )
        self.mock_use_case.handle.return_value = stock_response

        # Act
        result = self.command.execute(ticker)

        # Assert
        result_data = json.loads(result)
        assert result_data["data"]["price"] == "2847.123456789"

    def test_execute_returns_error_json_when_stock_not_found(self):
        """Test that execute() returns error JSON when stock is not found."""
        # Arrange
        ticker = "INVALID"
        self.mock_use_case.handle.side_effect = StockNotFound(ticker)

        # Act
        result = self.command.execute(ticker)

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["code"] == "STOCK_NOT_FOUND"
        assert ticker in result_data["error"]["message"]

    def test_execute_returns_error_json_on_unexpected_exception(self):
        """Test that execute() handles unexpected exceptions gracefully."""
        # Arrange
        ticker = "AAPL"
        error_message = "Database connection failed"
        self.mock_use_case.handle.side_effect = Exception(error_message)

        # Act
        result = self.command.execute(ticker)

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["code"] == "INTERNAL_ERROR"
        assert error_message in result_data["error"]["message"]

    def test_execute_calls_use_case_with_correct_ticker(self):
        """Test that execute() calls the use case with the correct ticker."""
        # Arrange
        ticker = "TSLA"
        stock_response = StockPriceResponse(
            ticker=ticker,
            price=Decimal("200.00"),
            currency="USD"
        )
        self.mock_use_case.handle.return_value = stock_response

        # Act
        self.command.execute(ticker)

        # Assert
        self.mock_use_case.handle.assert_called_once()
        call_args = self.mock_use_case.handle.call_args[0][0]
        assert call_args.ticker == ticker

    def test_execute_returns_valid_json_format(self):
        """Test that execute() always returns valid JSON."""
        # Arrange
        ticker = "MSFT"
        stock_response = StockPriceResponse(
            ticker=ticker,
            price=Decimal("350.50"),
            currency="USD"
        )
        self.mock_use_case.handle.return_value = stock_response

        # Act
        result = self.command.execute(ticker)

        # Assert
        try:
            json.loads(result)
        except json.JSONDecodeError:
            pytest.fail("Command did not return valid JSON")

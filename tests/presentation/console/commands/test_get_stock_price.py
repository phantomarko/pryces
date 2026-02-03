"""Unit tests for GetStockPriceCommand."""

import json
from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.application.exceptions import StockNotFound, StockInformationIncomplete
from pryces.application.providers import StockPriceResponse
from pryces.application.use_cases.get_stock_price import GetStockPrice
from pryces.presentation.console.commands.get_stock_price import (
    GetStockPriceCommand,
)


class TestGetStockPriceCommand:
    """Test suite for GetStockPriceCommand."""

    def setup_method(self):
        self.mock_use_case = Mock(spec=GetStockPrice)
        self.command = GetStockPriceCommand(self.mock_use_case)

    def test_execute_returns_success_json_with_stock_data(self):
        """Test that execute() returns success JSON when stock is found."""
        # Arrange
        symbol = "AAPL"
        stock_response = StockPriceResponse(
            symbol=symbol,
            name="Apple Inc.",
            currentPrice=Decimal("150.25"),
            currency="USD",
            previousClosePrice=Decimal("148.50"),
            openPrice=Decimal("149.00"),
            dayHigh=Decimal("151.00"),
            dayLow=Decimal("148.00"),
            fiftyDayAverage=Decimal("145.50"),
            twoHundredDayAverage=Decimal("140.00"),
            fiftyTwoWeekHigh=Decimal("180.00"),
            fiftyTwoWeekLow=Decimal("120.00")
        )
        self.mock_use_case.handle.return_value = stock_response

        # Act
        result = self.command.execute(symbol)

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"]["symbol"] == symbol
        assert result_data["data"]["currentPrice"] == "150.25"
        assert result_data["data"]["name"] == "Apple Inc."
        assert result_data["data"]["currency"] == "USD"

    def test_execute_handles_decimal_precision_in_json(self):
        """Test that execute() preserves Decimal precision in JSON output."""
        # Arrange
        symbol = "GOOGL"
        stock_response = StockPriceResponse(
            symbol=symbol,
            name="Alphabet Inc.",
            currentPrice=Decimal("2847.123456789"),
            currency="USD",
            previousClosePrice=Decimal("2830.00"),
            openPrice=Decimal("2835.00"),
            dayHigh=Decimal("2850.00"),
            dayLow=Decimal("2825.00"),
            fiftyDayAverage=Decimal("2800.00"),
            twoHundredDayAverage=Decimal("2750.00"),
            fiftyTwoWeekHigh=Decimal("3000.00"),
            fiftyTwoWeekLow=Decimal("2500.00")
        )
        self.mock_use_case.handle.return_value = stock_response

        # Act
        result = self.command.execute(symbol)

        # Assert
        result_data = json.loads(result)
        assert result_data["data"]["currentPrice"] == "2847.123456789"

    def test_execute_returns_error_json_when_stock_not_found(self):
        """Test that execute() returns error JSON when stock is not found."""
        # Arrange
        symbol = "INVALID"
        self.mock_use_case.handle.side_effect = StockNotFound(symbol)

        # Act
        result = self.command.execute(symbol)

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["code"] == "STOCK_NOT_FOUND"
        assert symbol in result_data["error"]["message"]

    def test_execute_returns_error_json_when_stock_information_incomplete(self):
        """Test that execute() returns error JSON when stock information is incomplete."""
        # Arrange
        symbol = "AAPL"
        self.mock_use_case.handle.side_effect = StockInformationIncomplete(symbol)

        # Act
        result = self.command.execute(symbol)

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["code"] == "INTERNAL_ERROR"
        assert "unable to retrieve current price" in result_data["error"]["message"]

    def test_execute_returns_error_json_on_unexpected_exception(self):
        """Test that execute() handles unexpected exceptions gracefully."""
        # Arrange
        symbol = "AAPL"
        error_message = "Database connection failed"
        self.mock_use_case.handle.side_effect = Exception(error_message)

        # Act
        result = self.command.execute(symbol)

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["code"] == "INTERNAL_ERROR"
        assert error_message in result_data["error"]["message"]

    def test_execute_calls_use_case_with_correct_symbol(self):
        """Test that execute() calls the use case with the correct symbol."""
        # Arrange
        symbol = "TSLA"
        stock_response = StockPriceResponse(
            symbol=symbol,
            name="Tesla, Inc.",
            currentPrice=Decimal("200.00"),
            currency="USD",
            previousClosePrice=Decimal("198.50"),
            openPrice=Decimal("199.00"),
            dayHigh=Decimal("202.00"),
            dayLow=Decimal("197.00"),
            fiftyDayAverage=Decimal("195.00"),
            twoHundredDayAverage=Decimal("190.00"),
            fiftyTwoWeekHigh=Decimal("250.00"),
            fiftyTwoWeekLow=Decimal("150.00")
        )
        self.mock_use_case.handle.return_value = stock_response

        # Act
        self.command.execute(symbol)

        # Assert
        self.mock_use_case.handle.assert_called_once()
        call_args = self.mock_use_case.handle.call_args[0][0]
        assert call_args.symbol == symbol

    def test_execute_returns_valid_json_format(self):
        """Test that execute() always returns valid JSON."""
        # Arrange
        symbol = "MSFT"
        stock_response = StockPriceResponse(
            symbol=symbol,
            name="Microsoft Corporation",
            currentPrice=Decimal("350.50"),
            currency="USD",
            previousClosePrice=Decimal("348.00"),
            openPrice=Decimal("349.00"),
            dayHigh=Decimal("352.00"),
            dayLow=Decimal("347.00"),
            fiftyDayAverage=Decimal("345.00"),
            twoHundredDayAverage=Decimal("340.00"),
            fiftyTwoWeekHigh=Decimal("380.00"),
            fiftyTwoWeekLow=Decimal("300.00")
        )
        self.mock_use_case.handle.return_value = stock_response

        # Act
        result = self.command.execute(symbol)

        # Assert
        try:
            json.loads(result)
        except json.JSONDecodeError:
            pytest.fail("Command did not return valid JSON")

    def test_execute_handles_response_with_minimal_fields(self):
        """Test that execute() properly serializes response with only required fields."""
        # Arrange
        symbol = "AAPL"
        minimal_response = StockPriceResponse(
            symbol=symbol,
            currentPrice=Decimal("150.25")
        )
        self.mock_use_case.handle.return_value = minimal_response

        # Act
        result = self.command.execute(symbol)

        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"]["symbol"] == symbol
        assert result_data["data"]["currentPrice"] == "150.25"
        assert result_data["data"]["name"] is None
        assert result_data["data"]["currency"] is None
        assert result_data["data"]["previousClosePrice"] is None

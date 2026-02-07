import json
from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.application.exceptions import StockInformationIncomplete
from pryces.application.interfaces import StockPriceProvider
from pryces.application.use_cases.get_stock_price import GetStockPrice
from pryces.presentation.console.commands.get_stock_price import (
    GetStockPriceCommand,
    validate_symbol,
)
from pryces.presentation.console.commands.base import CommandMetadata, InputPrompt
from tests.fixtures.factories import create_stock_price


class TestGetStockPriceCommand:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockPriceProvider)
        use_case = GetStockPrice(provider=self.mock_provider)
        self.command = GetStockPriceCommand(use_case)

    def test_execute_returns_success_json_with_stock_data(self):
        symbol = "AAPL"
        self.mock_provider.get_stock_price.return_value = create_stock_price(
            symbol,
            Decimal("150.25"),
            name="Apple Inc.",
            previousClosePrice=Decimal("148.50"),
            openPrice=Decimal("149.00"),
            dayHigh=Decimal("151.00"),
            dayLow=Decimal("148.00"),
            fiftyDayAverage=Decimal("145.50"),
            twoHundredDayAverage=Decimal("140.00"),
            fiftyTwoWeekHigh=Decimal("180.00"),
            fiftyTwoWeekLow=Decimal("120.00"),
        )

        result = self.command.execute(symbol)

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"]["symbol"] == symbol
        assert result_data["data"]["currentPrice"] == "150.25"
        assert result_data["data"]["name"] == "Apple Inc."
        assert result_data["data"]["currency"] == "USD"

    def test_execute_handles_decimal_precision_in_json(self):
        symbol = "GOOGL"
        self.mock_provider.get_stock_price.return_value = create_stock_price(
            symbol,
            Decimal("2847.123456789"),
            name="Alphabet Inc.",
            previousClosePrice=Decimal("2830.00"),
            openPrice=Decimal("2835.00"),
            dayHigh=Decimal("2850.00"),
            dayLow=Decimal("2825.00"),
            fiftyDayAverage=Decimal("2800.00"),
            twoHundredDayAverage=Decimal("2750.00"),
            fiftyTwoWeekHigh=Decimal("3000.00"),
            fiftyTwoWeekLow=Decimal("2500.00"),
        )

        result = self.command.execute(symbol)

        result_data = json.loads(result)
        assert result_data["data"]["currentPrice"] == "2847.123456789"

    def test_execute_returns_error_json_when_stock_not_found(self):
        symbol = "INVALID"
        self.mock_provider.get_stock_price.return_value = None

        result = self.command.execute(symbol)

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["code"] == "STOCK_NOT_FOUND"
        assert symbol in result_data["error"]["message"]

    def test_execute_returns_error_json_when_stock_information_incomplete(self):
        symbol = "AAPL"
        self.mock_provider.get_stock_price.side_effect = StockInformationIncomplete(symbol)

        result = self.command.execute(symbol)

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["code"] == "INTERNAL_ERROR"
        assert "unable to retrieve current price" in result_data["error"]["message"]

    def test_execute_returns_error_json_on_unexpected_exception(self):
        symbol = "AAPL"
        error_message = "Database connection failed"
        self.mock_provider.get_stock_price.side_effect = Exception(error_message)

        result = self.command.execute(symbol)

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["code"] == "INTERNAL_ERROR"
        assert error_message in result_data["error"]["message"]

    def test_execute_returns_valid_json_format(self):
        symbol = "MSFT"
        self.mock_provider.get_stock_price.return_value = create_stock_price(
            symbol,
            Decimal("350.50"),
            name="Microsoft Corporation",
            previousClosePrice=Decimal("348.00"),
            openPrice=Decimal("349.00"),
            dayHigh=Decimal("352.00"),
            dayLow=Decimal("347.00"),
            fiftyDayAverage=Decimal("345.00"),
            twoHundredDayAverage=Decimal("340.00"),
            fiftyTwoWeekHigh=Decimal("380.00"),
            fiftyTwoWeekLow=Decimal("300.00"),
        )

        result = self.command.execute(symbol)

        try:
            json.loads(result)
        except json.JSONDecodeError:
            pytest.fail("Command did not return valid JSON")

    def test_execute_handles_response_with_minimal_fields(self):
        symbol = "AAPL"
        self.mock_provider.get_stock_price.return_value = create_stock_price(
            symbol,
            Decimal("150.25"),
            name=None,
            currency=None,
            previousClosePrice=None,
            openPrice=None,
            dayHigh=None,
            dayLow=None,
            fiftyDayAverage=None,
            twoHundredDayAverage=None,
            fiftyTwoWeekHigh=None,
            fiftyTwoWeekLow=None,
        )

        result = self.command.execute(symbol)

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"]["symbol"] == symbol
        assert result_data["data"]["currentPrice"] == "150.25"
        assert result_data["data"]["name"] is None
        assert result_data["data"]["currency"] is None
        assert result_data["data"]["previousClosePrice"] is None

    def test_get_metadata_returns_correct_metadata(self):
        metadata = self.command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "get_stock_price"
        assert metadata.name == "Get Stock Price"
        assert "single stock symbol" in metadata.description

    def test_get_input_prompts_returns_symbol_prompt(self):
        prompts = self.command.get_input_prompts()

        assert len(prompts) == 1
        assert isinstance(prompts[0], InputPrompt)
        assert prompts[0].key == "symbol"
        assert "stock symbol" in prompts[0].prompt.lower()
        assert prompts[0].validator is validate_symbol

    def test_validate_symbol_accepts_valid_symbols(self):
        assert validate_symbol("AAPL") is True
        assert validate_symbol("GOOGL") is True
        assert validate_symbol("MSFT") is True
        assert validate_symbol("BRK.B") is True
        assert validate_symbol("TSM") is True

    def test_validate_symbol_rejects_invalid_symbols(self):
        assert validate_symbol("") is False
        assert validate_symbol("   ") is False
        assert validate_symbol("TOOLONGSYMBOL") is False

    def test_execute_accepts_kwargs_for_compatibility(self):
        symbol = "AAPL"
        self.mock_provider.get_stock_price.return_value = create_stock_price(
            symbol, Decimal("150.25"), name="Apple Inc."
        )

        result = self.command.execute(symbol=symbol, extra_arg="ignored")

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"]["symbol"] == symbol

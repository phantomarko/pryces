from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.application.interfaces import StockProvider
from pryces.application.use_cases.get_stock_price import GetStockPrice
from pryces.presentation.console.commands.get_stock_price import (
    GetStockPriceCommand,
    _validate_symbol,
)
from pryces.presentation.console.commands.base import CommandMetadata, InputPrompt
from tests.fixtures.factories import create_stock


class TestGetStockPriceCommand:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockProvider)
        use_case = GetStockPrice(provider=self.mock_provider)
        self.command = GetStockPriceCommand(use_case)

    def test_execute_returns_formatted_stock_data(self):
        symbol = "AAPL"
        self.mock_provider.get_stock.return_value = create_stock(
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

        assert "AAPL - Apple Inc. (USD)" in result
        assert "Current Price:" in result
        assert "150.25" in result
        assert "Previous Close:" in result
        assert "148.50" in result

    def test_execute_preserves_decimal_precision(self):
        symbol = "GOOGL"
        self.mock_provider.get_stock.return_value = create_stock(
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

        assert "2847.123456789" in result

    def test_execute_returns_error_when_stock_not_found(self):
        symbol = "INVALID"
        self.mock_provider.get_stock.return_value = None

        result = self.command.execute(symbol)

        assert result.startswith("Error:")
        assert symbol in result

    def test_execute_returns_error_on_unexpected_exception(self):
        symbol = "AAPL"
        error_message = "Database connection failed"
        self.mock_provider.get_stock.side_effect = Exception(error_message)

        result = self.command.execute(symbol)

        assert result.startswith("Error:")
        assert error_message in result

    def test_execute_handles_response_with_minimal_fields(self):
        symbol = "AAPL"
        self.mock_provider.get_stock.return_value = create_stock(
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

        assert result.startswith("AAPL\n")
        assert "Current Price:" in result
        assert "150.25" in result
        assert "Previous Close:" not in result

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
        assert prompts[0].validator is _validate_symbol

    def test_validate_symbol_accepts_valid_symbols(self):
        assert _validate_symbol("AAPL") is True
        assert _validate_symbol("GOOGL") is True
        assert _validate_symbol("MSFT") is True
        assert _validate_symbol("BRK.B") is True
        assert _validate_symbol("TSM") is True

    def test_validate_symbol_rejects_invalid_symbols(self):
        assert _validate_symbol("") is False
        assert _validate_symbol("   ") is False
        assert _validate_symbol("TOOLONGSYMBOL") is False

    def test_execute_accepts_kwargs_for_compatibility(self):
        symbol = "AAPL"
        self.mock_provider.get_stock.return_value = create_stock(
            symbol, Decimal("150.25"), name="Apple Inc."
        )

        result = self.command.execute(symbol=symbol, extra_arg="ignored")

        assert "AAPL - Apple Inc. (USD)" in result
        assert "Current Price:" in result

from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.application.interfaces import StockProvider
from pryces.application.use_cases.get_stocks_prices import GetStocksPrices
from pryces.presentation.console.commands.get_stocks_prices import GetStocksPricesCommand
from pryces.presentation.console.utils import validate_symbols
from pryces.presentation.console.commands.base import CommandMetadata, InputPrompt
from tests.fixtures.factories import create_stock


class TestGetStocksPricesCommand:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockProvider)
        use_case = GetStocksPrices(provider=self.mock_provider)
        self.command = GetStocksPricesCommand(use_case)

    def test_execute_returns_formatted_multiple_stocks(self):
        symbols = "AAPL,GOOGL,MSFT"
        self.mock_provider.get_stocks.return_value = [
            create_stock("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
            create_stock("MSFT", Decimal("350.75"), name="Microsoft Corporation"),
        ]

        result = self.command.execute(symbols)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "GOOGL - Alphabet Inc. (USD)" in result
        assert "MSFT - Microsoft Corporation (USD)" in result
        assert "Summary: 3 requested, 3 successful, 0 failed" in result

    def test_execute_handles_partial_failures(self):
        symbols = "AAPL,INVALID,GOOGL"
        self.mock_provider.get_stocks.return_value = [
            create_stock("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
        ]

        result = self.command.execute(symbols)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "GOOGL - Alphabet Inc. (USD)" in result
        assert "Summary: 3 requested, 2 successful, 1 failed" in result

    def test_execute_handles_all_failures(self):
        symbols = "INVALID1,INVALID2,INVALID3"
        self.mock_provider.get_stocks.return_value = []

        result = self.command.execute(symbols)

        assert "Summary: 3 requested, 0 successful, 3 failed" in result

    def test_execute_preserves_decimal_precision(self):
        symbols = "GOOGL"
        self.mock_provider.get_stocks.return_value = [
            create_stock("GOOGL", Decimal("2847.123456789"), name="Alphabet Inc.")
        ]

        result = self.command.execute(symbols)

        assert "2847.123456789" in result

    def test_execute_returns_error_on_unexpected_exception(self):
        symbols = "AAPL,GOOGL"
        error_message = "Network connection failed"
        self.mock_provider.get_stocks.side_effect = Exception(error_message)

        result = self.command.execute(symbols)

        assert result.startswith("Error:")
        assert error_message in result

    def test_execute_handles_responses_with_minimal_fields(self):
        symbols = "AAPL,GOOGL"
        self.mock_provider.get_stocks.return_value = [
            create_stock(
                "AAPL",
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
            ),
            create_stock(
                "GOOGL",
                Decimal("2847.50"),
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
            ),
        ]

        result = self.command.execute(symbols)

        assert "AAPL\n" in result
        assert "GOOGL\n" in result
        assert "Current Price:" in result
        assert "Previous Close:" not in result

    def test_execute_handles_responses_with_all_fields(self):
        symbols = "AAPL"
        self.mock_provider.get_stocks.return_value = [
            create_stock(
                "AAPL",
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
        ]

        result = self.command.execute(symbols)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "Previous Close:" in result
        assert "148.50" in result
        assert "Open:" in result
        assert "149.00" in result
        assert "Day High:" in result
        assert "151.00" in result
        assert "Day Low:" in result
        assert "148.00" in result
        assert "50-Day Average:" in result
        assert "145.50" in result
        assert "200-Day Average:" in result
        assert "140.00" in result
        assert "52-Week High:" in result
        assert "180.00" in result
        assert "52-Week Low:" in result
        assert "120.00" in result

    def test_get_metadata_returns_correct_metadata(self):
        metadata = self.command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "get_stocks_prices"
        assert metadata.name == "Get Multiple Stock Prices"
        assert "multiple stock symbols" in metadata.description

    def test_get_input_prompts_returns_symbols_prompt(self):
        prompts = self.command.get_input_prompts()

        assert len(prompts) == 1
        assert isinstance(prompts[0], InputPrompt)
        assert prompts[0].key == "symbols"
        assert "commas" in prompts[0].prompt.lower()
        assert prompts[0].validator is validate_symbols

    def test_execute_accepts_kwargs_for_compatibility(self):
        symbols = "AAPL,GOOGL"
        self.mock_provider.get_stocks.return_value = [
            create_stock("AAPL", Decimal("150.25")),
            create_stock("GOOGL", Decimal("2847.50")),
        ]

        result = self.command.execute(symbols=symbols, extra_arg="ignored")

        assert "AAPL" in result
        assert "GOOGL" in result
        assert "Summary: 2 requested, 2 successful, 0 failed" in result

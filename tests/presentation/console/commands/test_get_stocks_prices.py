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
        self.command = GetStocksPricesCommand(use_case, logger_factory=Mock())

    def test_execute_returns_formatted_multiple_stocks(self):
        symbols = "AAPL GOOGL MSFT"
        self.mock_provider.get_stocks.return_value = [
            create_stock("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
            create_stock("MSFT", Decimal("350.75"), name="Microsoft Corporation"),
        ]

        result = self.command.execute(symbols)

        assert "AAPL - Apple Inc. (USD)" in result.message
        assert "GOOGL - Alphabet Inc. (USD)" in result.message
        assert "MSFT - Microsoft Corporation (USD)" in result.message
        assert "Summary: 3 requested, 3 successful, 0 failed" in result.message

    def test_execute_handles_partial_failures(self):
        symbols = "AAPL INVALID GOOGL"
        self.mock_provider.get_stocks.return_value = [
            create_stock("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
        ]

        result = self.command.execute(symbols)

        assert "AAPL - Apple Inc. (USD)" in result.message
        assert "GOOGL - Alphabet Inc. (USD)" in result.message
        assert "Summary: 3 requested, 2 successful, 1 failed" in result.message

    def test_execute_handles_all_failures(self):
        symbols = "INVALID1 INVALID2 INVALID3"
        self.mock_provider.get_stocks.return_value = []

        result = self.command.execute(symbols)

        assert "Summary: 3 requested, 0 successful, 3 failed" in result.message

    def test_execute_preserves_decimal_precision(self):
        symbols = "GOOGL"
        self.mock_provider.get_stocks.return_value = [
            create_stock("GOOGL", Decimal("2847.123456789"), name="Alphabet Inc.")
        ]

        result = self.command.execute(symbols)

        assert "2847.123456789" in result.message

    def test_execute_returns_error_on_unexpected_exception(self):
        symbols = "AAPL GOOGL"
        error_message = "Network connection failed"
        self.mock_provider.get_stocks.side_effect = Exception(error_message)

        result = self.command.execute(symbols)

        assert result.message.startswith("Error:")
        assert error_message in result.message
        assert result.success is False

    def test_execute_handles_responses_with_minimal_fields(self):
        symbols = "AAPL GOOGL"
        self.mock_provider.get_stocks.return_value = [
            create_stock(
                "AAPL",
                Decimal("150.25"),
                name=None,
                currency=None,
                previous_close_price=None,
                open_price=None,
                day_high=None,
                day_low=None,
                fifty_day_average=None,
                two_hundred_day_average=None,
                fifty_two_week_high=None,
                fifty_two_week_low=None,
            ),
            create_stock(
                "GOOGL",
                Decimal("2847.50"),
                name=None,
                currency=None,
                previous_close_price=None,
                open_price=None,
                day_high=None,
                day_low=None,
                fifty_day_average=None,
                two_hundred_day_average=None,
                fifty_two_week_high=None,
                fifty_two_week_low=None,
            ),
        ]

        result = self.command.execute(symbols)

        assert "AAPL\n" in result.message
        assert "GOOGL\n" in result.message
        assert "Current Price:" in result.message
        assert "Previous Close:" not in result.message

    def test_execute_handles_responses_with_all_fields(self):
        symbols = "AAPL"
        self.mock_provider.get_stocks.return_value = [
            create_stock(
                "AAPL",
                Decimal("150.25"),
                name="Apple Inc.",
                previous_close_price=Decimal("148.50"),
                open_price=Decimal("149.00"),
                day_high=Decimal("151.00"),
                day_low=Decimal("148.00"),
                fifty_day_average=Decimal("145.50"),
                two_hundred_day_average=Decimal("140.00"),
                fifty_two_week_high=Decimal("180.00"),
                fifty_two_week_low=Decimal("120.00"),
            )
        ]

        result = self.command.execute(symbols)

        assert "AAPL - Apple Inc. (USD)" in result.message
        assert "Previous Close:" in result.message
        assert "148.50" in result.message
        assert "Open:" in result.message
        assert "149.00" in result.message
        assert "Day High:" in result.message
        assert "151.00" in result.message
        assert "Day Low:" in result.message
        assert "148.00" in result.message
        assert "50-Day Average:" in result.message
        assert "145.50" in result.message
        assert "200-Day Average:" in result.message
        assert "140.00" in result.message
        assert "52-Week High:" in result.message
        assert "180.00" in result.message
        assert "52-Week Low:" in result.message
        assert "120.00" in result.message

    def test_get_metadata_returns_correct_metadata(self):
        metadata = self.command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "get_stocks_prices"
        assert metadata.name == "Get Stock Prices"
        assert "multiple stock symbols" in metadata.description

    def test_get_input_prompts_returns_symbols_prompt(self):
        prompts = self.command.get_input_prompts()

        assert len(prompts) == 1
        assert isinstance(prompts[0], InputPrompt)
        assert prompts[0].key == "symbols"
        assert "spaces" in prompts[0].prompt.lower()
        assert prompts[0].validator is validate_symbols

    def test_execute_accepts_kwargs_for_compatibility(self):
        symbols = "AAPL GOOGL"
        self.mock_provider.get_stocks.return_value = [
            create_stock("AAPL", Decimal("150.25")),
            create_stock("GOOGL", Decimal("2847.50")),
        ]

        result = self.command.execute(symbols=symbols, extra_arg="ignored")

        assert "AAPL" in result.message
        assert "GOOGL" in result.message
        assert "Summary: 2 requested, 2 successful, 0 failed" in result.message

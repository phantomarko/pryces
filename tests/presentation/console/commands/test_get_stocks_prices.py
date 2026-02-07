import json
from decimal import Decimal
from unittest.mock import Mock

import pytest

from pryces.application.dtos import StockPriceDTO
from pryces.application.use_cases.get_stocks_prices import GetStocksPrices
from pryces.presentation.console.commands.get_stocks_prices import (
    GetStocksPricesCommand,
    validate_symbols,
    parse_symbols_input,
)
from pryces.presentation.console.commands.base import CommandMetadata, InputPrompt
from tests.fixtures.factories import create_stock_price_dto


class TestGetStocksPricesCommand:

    def setup_method(self):
        self.mock_use_case = Mock(spec=GetStocksPrices)
        self.command = GetStocksPricesCommand(self.mock_use_case)

    def test_execute_returns_success_json_with_multiple_stocks(self):
        symbols = "AAPL,GOOGL,MSFT"
        stock_responses = [
            create_stock_price_dto("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock_price_dto("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
            create_stock_price_dto("MSFT", Decimal("350.75"), name="Microsoft Corporation"),
        ]
        self.mock_use_case.handle.return_value = stock_responses

        result = self.command.execute(symbols)

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["data"]) == 3
        assert result_data["data"][0]["symbol"] == "AAPL"
        assert result_data["data"][1]["symbol"] == "GOOGL"
        assert result_data["data"][2]["symbol"] == "MSFT"
        assert result_data["summary"]["requested"] == 3
        assert result_data["summary"]["successful"] == 3
        assert result_data["summary"]["failed"] == 0

    def test_execute_handles_partial_failures(self):
        symbols = "AAPL,INVALID,GOOGL"
        stock_responses = [
            create_stock_price_dto("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock_price_dto("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
        ]
        self.mock_use_case.handle.return_value = stock_responses

        result = self.command.execute(symbols)

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["data"]) == 2
        assert result_data["summary"]["requested"] == 3
        assert result_data["summary"]["successful"] == 2
        assert result_data["summary"]["failed"] == 1

    def test_execute_handles_all_failures(self):
        symbols = "INVALID1,INVALID2,INVALID3"
        stock_responses = []
        self.mock_use_case.handle.return_value = stock_responses

        result = self.command.execute(symbols)

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["data"]) == 0
        assert result_data["summary"]["requested"] == 3
        assert result_data["summary"]["successful"] == 0
        assert result_data["summary"]["failed"] == 3

    def test_execute_handles_decimal_precision_in_json(self):
        symbols = "GOOGL"
        stock_responses = [
            create_stock_price_dto("GOOGL", Decimal("2847.123456789"), name="Alphabet Inc.")
        ]
        self.mock_use_case.handle.return_value = stock_responses

        result = self.command.execute(symbols)

        result_data = json.loads(result)
        assert result_data["data"][0]["currentPrice"] == "2847.123456789"

    def test_execute_returns_error_json_on_unexpected_exception(self):
        symbols = "AAPL,GOOGL"
        error_message = "Network connection failed"
        self.mock_use_case.handle.side_effect = Exception(error_message)

        result = self.command.execute(symbols)

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert result_data["error"]["code"] == "INTERNAL_ERROR"
        assert error_message in result_data["error"]["message"]

    def test_execute_calls_use_case_with_correct_symbols(self):
        symbols = "AAPL, GOOGL, MSFT"
        stock_responses = [
            create_stock_price_dto("AAPL", Decimal("150.25")),
            create_stock_price_dto("GOOGL", Decimal("2847.50")),
            create_stock_price_dto("MSFT", Decimal("350.75")),
        ]
        self.mock_use_case.handle.return_value = stock_responses

        self.command.execute(symbols)

        self.mock_use_case.handle.assert_called_once()
        call_args = self.mock_use_case.handle.call_args[0][0]
        assert call_args.symbols == ["AAPL", "GOOGL", "MSFT"]

    def test_execute_returns_valid_json_format(self):
        symbols = "AAPL,GOOGL"
        stock_responses = [
            create_stock_price_dto("AAPL", Decimal("150.25")),
            create_stock_price_dto("GOOGL", Decimal("2847.50")),
        ]
        self.mock_use_case.handle.return_value = stock_responses

        result = self.command.execute(symbols)

        try:
            json.loads(result)
        except json.JSONDecodeError:
            pytest.fail("Command did not return valid JSON")

    def test_execute_handles_responses_with_minimal_fields(self):
        symbols = "AAPL,GOOGL"
        minimal_responses = [
            StockPriceDTO(symbol="AAPL", currentPrice=Decimal("150.25")),
            StockPriceDTO(symbol="GOOGL", currentPrice=Decimal("2847.50")),
        ]
        self.mock_use_case.handle.return_value = minimal_responses

        result = self.command.execute(symbols)

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"][0]["symbol"] == "AAPL"
        assert result_data["data"][0]["currentPrice"] == "150.25"
        assert result_data["data"][0]["name"] is None
        assert result_data["data"][0]["currency"] is None

    def test_execute_handles_responses_with_all_fields(self):
        symbols = "AAPL"
        complete_response = [
            create_stock_price_dto(
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
        self.mock_use_case.handle.return_value = complete_response

        result = self.command.execute(symbols)

        result_data = json.loads(result)
        data = result_data["data"][0]
        assert data["name"] == "Apple Inc."
        assert data["currency"] == "USD"
        assert data["previousClosePrice"] == "148.50"
        assert data["openPrice"] == "149.00"
        assert data["dayHigh"] == "151.00"
        assert data["dayLow"] == "148.00"
        assert data["fiftyDayAverage"] == "145.50"
        assert data["twoHundredDayAverage"] == "140.00"
        assert data["fiftyTwoWeekHigh"] == "180.00"
        assert data["fiftyTwoWeekLow"] == "120.00"

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
        stock_responses = [
            create_stock_price_dto("AAPL", Decimal("150.25")),
            create_stock_price_dto("GOOGL", Decimal("2847.50")),
        ]
        self.mock_use_case.handle.return_value = stock_responses

        result = self.command.execute(symbols=symbols, extra_arg="ignored")

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["data"]) == 2


class TestValidateSymbols:

    def test_accepts_valid_single_symbol(self):
        assert validate_symbols("AAPL") is True

    def test_accepts_valid_comma_separated_symbols(self):
        assert validate_symbols("AAPL,GOOGL,MSFT") is True

    def test_accepts_symbols_with_spaces(self):
        assert validate_symbols("AAPL, GOOGL, MSFT") is True
        assert validate_symbols("AAPL , GOOGL , MSFT") is True

    def test_rejects_empty_string(self):
        assert validate_symbols("") is False
        assert validate_symbols("   ") is False

    def test_rejects_symbols_too_long(self):
        assert validate_symbols("TOOLONGSYMBOL") is False
        assert validate_symbols("AAPL,TOOLONGSYMBOL") is False

    def test_rejects_empty_symbols_in_list(self):
        assert validate_symbols("AAPL,,GOOGL") is False
        assert validate_symbols(",AAPL,GOOGL") is False
        assert validate_symbols("AAPL,GOOGL,") is False


class TestParseSymbolsInput:

    def test_parses_single_symbol(self):
        result = parse_symbols_input("AAPL")
        assert result == ["AAPL"]

    def test_parses_comma_separated_symbols(self):
        result = parse_symbols_input("AAPL,GOOGL,MSFT")
        assert result == ["AAPL", "GOOGL", "MSFT"]

    def test_strips_whitespace(self):
        result = parse_symbols_input("AAPL, GOOGL, MSFT")
        assert result == ["AAPL", "GOOGL", "MSFT"]

    def test_converts_to_uppercase(self):
        result = parse_symbols_input("aapl,googl,msft")
        assert result == ["AAPL", "GOOGL", "MSFT"]

    def test_filters_empty_strings(self):
        result = parse_symbols_input("AAPL,,GOOGL")
        assert result == ["AAPL", "GOOGL"]

    def test_handles_mixed_case_with_spaces(self):
        result = parse_symbols_input("aapl, GooGl, MsFt")
        assert result == ["AAPL", "GOOGL", "MSFT"]

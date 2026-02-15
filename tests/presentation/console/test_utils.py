from decimal import Decimal

from pryces.presentation.console.utils import (
    format_stock,
    format_stock_list,
    parse_symbols_input,
    validate_file_path,
    validate_positive_integer,
    validate_symbol,
    validate_symbols,
)
from tests.fixtures.factories import create_stock_dto


class TestValidateSymbol:

    def test_accepts_valid_symbols(self):
        assert validate_symbol("AAPL") is True
        assert validate_symbol("GOOGL") is True
        assert validate_symbol("MSFT") is True
        assert validate_symbol("BRK.B") is True
        assert validate_symbol("TSM") is True

    def test_rejects_invalid_symbols(self):
        assert validate_symbol("") is False
        assert validate_symbol("   ") is False
        assert validate_symbol("TOOLONGSYMBOL") is False


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


class TestValidatePositiveInteger:

    def test_accepts_positive_integers(self):
        assert validate_positive_integer("1") is True
        assert validate_positive_integer("10") is True
        assert validate_positive_integer("300") is True

    def test_rejects_zero(self):
        assert validate_positive_integer("0") is False

    def test_rejects_negative_numbers(self):
        assert validate_positive_integer("-1") is False
        assert validate_positive_integer("-100") is False

    def test_rejects_non_numeric(self):
        assert validate_positive_integer("abc") is False
        assert validate_positive_integer("") is False
        assert validate_positive_integer("1.5") is False

    def test_rejects_none(self):
        assert validate_positive_integer(None) is False


class TestValidateFilePath:

    def test_accepts_existing_file(self, tmp_path):
        file = tmp_path / "config.json"
        file.write_text("{}")

        assert validate_file_path(str(file)) is True

    def test_accepts_existing_file_with_whitespace(self, tmp_path):
        file = tmp_path / "config.json"
        file.write_text("{}")

        assert validate_file_path(f"  {file}  ") is True

    def test_rejects_nonexistent_path(self):
        assert validate_file_path("/nonexistent/path/to/file.json") is False

    def test_rejects_directory(self, tmp_path):
        assert validate_file_path(str(tmp_path)) is False

    def test_rejects_empty_string(self):
        assert validate_file_path("") is False

    def test_rejects_whitespace_only(self):
        assert validate_file_path("   ") is False


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


class TestFormatStock:

    def test_formats_stock_with_all_fields(self):
        dto = create_stock_dto(
            "AAPL",
            Decimal("150.25"),
            name="Apple Inc.",
            currency="USD",
            previousClosePrice=Decimal("148.50"),
            openPrice=Decimal("149.00"),
            dayHigh=Decimal("151.00"),
            dayLow=Decimal("148.00"),
            fiftyDayAverage=Decimal("145.50"),
            twoHundredDayAverage=Decimal("140.00"),
            fiftyTwoWeekHigh=Decimal("180.00"),
            fiftyTwoWeekLow=Decimal("120.00"),
        )

        result = format_stock(dto)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "Current Price:" in result
        assert "150.25" in result
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

    def test_formats_stock_with_minimal_fields(self):
        dto = create_stock_dto(
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
        )

        result = format_stock(dto)

        assert result.startswith("AAPL\n")
        assert "Current Price:" in result
        assert "150.25" in result
        assert "Previous Close:" not in result
        assert "Open:" not in result

    def test_omits_none_fields(self):
        dto = create_stock_dto(
            "AAPL",
            Decimal("150.25"),
            name="Apple Inc.",
            previousClosePrice=Decimal("148.50"),
            openPrice=None,
            dayHigh=None,
            dayLow=None,
            fiftyDayAverage=None,
            twoHundredDayAverage=None,
            fiftyTwoWeekHigh=None,
            fiftyTwoWeekLow=None,
        )

        result = format_stock(dto)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "Current Price:" in result
        assert "Previous Close:" in result
        assert "Open:" not in result
        assert "Day High:" not in result

    def test_header_without_name(self):
        dto = create_stock_dto("AAPL", Decimal("150.25"), name=None)

        result = format_stock(dto)

        lines = result.split("\n")
        assert lines[0] == "AAPL (USD)"

    def test_header_without_currency(self):
        dto = create_stock_dto("AAPL", Decimal("150.25"), name="Apple Inc.", currency=None)

        result = format_stock(dto)

        lines = result.split("\n")
        assert lines[0] == "AAPL - Apple Inc."

    def test_does_not_include_notifications(self):
        dto = create_stock_dto("AAPL", Decimal("150.25"))

        result = format_stock(dto)

        assert "notification" not in result.lower()

    def test_preserves_decimal_precision(self):
        dto = create_stock_dto(
            "GOOGL",
            Decimal("2847.123456789"),
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

        result = format_stock(dto)

        assert "2847.123456789" in result


class TestFormatStockList:

    def test_formats_multiple_stocks_with_separators(self):
        dtos = [
            create_stock_dto("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock_dto("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
        ]

        result = format_stock_list(dtos, requested_count=2)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "GOOGL - Alphabet Inc. (USD)" in result
        assert "------------------------------------------------------------" in result
        assert "============================================================" in result
        assert "Summary: 2 requested, 2 successful, 0 failed" in result

    def test_formats_single_stock_with_summary(self):
        dtos = [create_stock_dto("AAPL", Decimal("150.25"), name="Apple Inc.")]

        result = format_stock_list(dtos, requested_count=1)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "------------------------------------------------------------" not in result
        assert "============================================================" in result
        assert "Summary: 1 requested, 1 successful, 0 failed" in result

    def test_formats_partial_failures(self):
        dtos = [
            create_stock_dto("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock_dto("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
        ]

        result = format_stock_list(dtos, requested_count=3)

        assert "Summary: 3 requested, 2 successful, 1 failed" in result

    def test_formats_all_failures(self):
        result = format_stock_list([], requested_count=3)

        assert "============================================================" not in result
        assert "Summary: 3 requested, 0 successful, 3 failed" in result

    def test_three_stocks_have_two_separators(self):
        dtos = [
            create_stock_dto("AAPL", Decimal("150.25")),
            create_stock_dto("GOOGL", Decimal("2847.50")),
            create_stock_dto("MSFT", Decimal("350.75")),
        ]

        result = format_stock_list(dtos, requested_count=3)

        assert result.count("------------------------------------------------------------") == 2
        assert "Summary: 3 requested, 3 successful, 0 failed" in result

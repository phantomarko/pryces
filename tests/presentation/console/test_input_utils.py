from pryces.presentation.console.input_utils import (
    parse_symbols_input,
    validate_positive_integer,
    validate_symbol,
    validate_symbols,
)


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

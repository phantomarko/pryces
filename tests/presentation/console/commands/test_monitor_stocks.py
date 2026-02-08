from decimal import Decimal
from unittest.mock import Mock

from pryces.application.interfaces import MessageSender, StockProvider
from pryces.application.use_cases.trigger_stocks_notifications import TriggerStocksNotifications
from pryces.presentation.console.commands.base import CommandMetadata, InputPrompt
from pryces.presentation.console.commands.monitor_stocks import (
    MonitorStocksCommand,
    validate_symbols,
    parse_symbols_input,
)
from tests.fixtures.factories import (
    create_stock_crossing_both_averages,
    create_stock_crossing_fifty_day,
    create_stock_crossing_two_hundred_day,
    create_stock_no_crossing,
)


class TestMonitorStocksCommand:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockProvider)
        self.mock_sender = Mock(spec=MessageSender)
        use_case = TriggerStocksNotifications(provider=self.mock_provider, sender=self.mock_sender)
        self.command = MonitorStocksCommand(use_case)

    def test_get_metadata_returns_correct_metadata(self):
        metadata = self.command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "monitor_stocks"
        assert metadata.name == "Monitor Stocks"

    def test_get_input_prompts_returns_symbols_prompt(self):
        prompts = self.command.get_input_prompts()

        assert len(prompts) == 1
        assert isinstance(prompts[0], InputPrompt)
        assert prompts[0].key == "symbols"
        assert "commas" in prompts[0].prompt.lower()
        assert prompts[0].validator is validate_symbols

    def test_execute_with_notifications_returns_correct_summary(self):
        stock = create_stock_crossing_fifty_day("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]

        result = self.command.execute("AAPL")

        assert "1 stocks checked" in result
        assert "1 notifications sent" in result
        self.mock_sender.send_message.assert_called_once()

    def test_execute_without_notifications_returns_zero_notifications(self):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]

        result = self.command.execute("AAPL")

        assert "1 stocks checked" in result
        assert "0 notifications sent" in result
        self.mock_sender.send_message.assert_not_called()

    def test_execute_with_mixed_stocks(self):
        crossing_stock = create_stock_crossing_fifty_day("AAPL")
        no_crossing_stock = create_stock_no_crossing("GOOGL")
        self.mock_provider.get_stocks.return_value = [crossing_stock, no_crossing_stock]

        result = self.command.execute("AAPL,GOOGL")

        assert "2 stocks checked" in result
        assert "1 notifications sent" in result
        self.mock_sender.send_message.assert_called_once()

    def test_execute_with_both_crossings(self):
        stock = create_stock_crossing_both_averages("MSFT")
        self.mock_provider.get_stocks.return_value = [stock]

        result = self.command.execute("MSFT")

        assert "1 stocks checked" in result
        assert "2 notifications sent" in result
        assert self.mock_sender.send_message.call_count == 2

    def test_execute_with_two_hundred_day_crossing(self):
        stock = create_stock_crossing_two_hundred_day("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock]

        result = self.command.execute("GOOGL")

        assert "1 stocks checked" in result
        assert "1 notifications sent" in result
        self.mock_sender.send_message.assert_called_once()

    def test_execute_returns_failure_message_on_exception(self):
        error_message = "Network connection failed"
        self.mock_provider.get_stocks.side_effect = Exception(error_message)

        result = self.command.execute("AAPL")

        assert "Monitoring failed:" in result
        assert error_message in result

    def test_execute_with_empty_results(self):
        self.mock_provider.get_stocks.return_value = []

        result = self.command.execute("INVALID")

        assert "0 stocks checked" in result
        assert "0 notifications sent" in result

    def test_execute_accepts_kwargs_for_compatibility(self):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]

        result = self.command.execute(symbols="AAPL", extra_arg="ignored")

        assert "Monitoring complete" in result


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

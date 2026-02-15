from unittest.mock import Mock, patch

from pryces.application.interfaces import MessageSender, StockProvider
from pryces.application.services import NotificationService
from pryces.application.use_cases.trigger_stocks_notifications import TriggerStocksNotifications
from pryces.presentation.console.commands.base import CommandMetadata, InputPrompt
from pryces.presentation.console.commands.monitor_stocks import MonitorStocksCommand
from pryces.presentation.console.utils import (
    validate_positive_integer,
    validate_symbols,
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
        self.mock_notification_service = NotificationService(self.mock_sender)
        use_case = TriggerStocksNotifications(
            provider=self.mock_provider, notification_service=self.mock_notification_service
        )
        self.command = MonitorStocksCommand(use_case)

    def test_get_metadata_returns_correct_metadata(self):
        metadata = self.command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "monitor_stocks"
        assert metadata.name == "Monitor Stocks"

    def test_get_input_prompts_returns_symbols_interval_and_duration(self):
        prompts = self.command.get_input_prompts()

        assert len(prompts) == 3
        assert isinstance(prompts[0], InputPrompt)
        assert prompts[0].key == "symbols"
        assert "commas" in prompts[0].prompt.lower()
        assert prompts[0].validator is validate_symbols
        assert prompts[1].key == "interval"
        assert prompts[1].validator is validate_positive_integer
        assert prompts[2].key == "duration"
        assert "minutes" in prompts[2].prompt.lower()
        assert prompts[2].validator is validate_positive_integer

    @patch("pryces.presentation.console.commands.monitor_stocks.time.monotonic")
    def test_execute_with_notifications_returns_correct_summary(self, mock_monotonic):
        stock = create_stock_crossing_fifty_day("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        mock_monotonic.side_effect = [0, 60]

        result = self.command.execute(symbols="AAPL", interval="90", duration="1")

        assert "1 stocks checked" in result
        assert self.mock_sender.send_message.call_count == 2

    @patch("pryces.presentation.console.commands.monitor_stocks.time.monotonic")
    def test_execute_without_crossings_returns_market_open_notification(self, mock_monotonic):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        mock_monotonic.side_effect = [0, 60]

        result = self.command.execute(symbols="AAPL", interval="90", duration="1")

        assert "1 stocks checked" in result
        self.mock_sender.send_message.assert_called_once()

    @patch("pryces.presentation.console.commands.monitor_stocks.time.monotonic")
    def test_execute_with_mixed_stocks(self, mock_monotonic):
        crossing_stock = create_stock_crossing_fifty_day("AAPL")
        no_crossing_stock = create_stock_no_crossing("GOOGL")
        self.mock_provider.get_stocks.return_value = [crossing_stock, no_crossing_stock]
        mock_monotonic.side_effect = [0, 60]

        result = self.command.execute(symbols="AAPL,GOOGL", interval="90", duration="1")

        assert "2 stocks checked" in result
        assert self.mock_sender.send_message.call_count == 3

    @patch("pryces.presentation.console.commands.monitor_stocks.time.monotonic")
    def test_execute_with_both_crossings(self, mock_monotonic):
        stock = create_stock_crossing_both_averages("MSFT")
        self.mock_provider.get_stocks.return_value = [stock]
        mock_monotonic.side_effect = [0, 60]

        result = self.command.execute(symbols="MSFT", interval="90", duration="1")

        assert "1 stocks checked" in result
        assert self.mock_sender.send_message.call_count == 3

    @patch("pryces.presentation.console.commands.monitor_stocks.time.monotonic")
    def test_execute_with_two_hundred_day_crossing(self, mock_monotonic):
        stock = create_stock_crossing_two_hundred_day("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock]
        mock_monotonic.side_effect = [0, 60]

        result = self.command.execute(symbols="GOOGL", interval="90", duration="1")

        assert "1 stocks checked" in result
        assert self.mock_sender.send_message.call_count == 3

    @patch("pryces.presentation.console.commands.monitor_stocks.time.monotonic")
    def test_execute_continues_on_exception(self, mock_monotonic):
        self.mock_provider.get_stocks.side_effect = Exception("Network connection failed")
        mock_monotonic.side_effect = [0, 60]

        result = self.command.execute(symbols="AAPL", interval="90", duration="1")

        assert "Monitoring complete" in result

    @patch("pryces.presentation.console.commands.monitor_stocks.time.monotonic")
    def test_execute_with_empty_results(self, mock_monotonic):
        self.mock_provider.get_stocks.return_value = []
        mock_monotonic.side_effect = [0, 60]

        result = self.command.execute(symbols="INVALID", interval="90", duration="1")

        assert "1 stocks checked" in result

    @patch("pryces.presentation.console.commands.monitor_stocks.time.monotonic")
    def test_execute_accepts_kwargs_for_compatibility(self, mock_monotonic):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        mock_monotonic.side_effect = [0, 60]

        result = self.command.execute(
            symbols="AAPL", interval="90", duration="1", extra_arg="ignored"
        )

        assert "Monitoring complete" in result

    @patch("pryces.presentation.console.commands.monitor_stocks.time.sleep")
    @patch("pryces.presentation.console.commands.monitor_stocks.time.monotonic")
    def test_execute_with_multiple_cycles(self, mock_monotonic, mock_sleep):
        stock = create_stock_crossing_fifty_day("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        # monotonic calls: start(0), elapsed_check(30<180), elapsed_check(90<180),
        #                  elapsed_check(150<180), elapsed_check(210>=180) → break
        mock_monotonic.side_effect = [0, 30, 90, 150, 210]

        result = self.command.execute(symbols="AAPL", interval="60", duration="3")

        assert self.mock_provider.get_stocks.call_count == 4
        assert mock_sleep.call_count == 3
        mock_sleep.assert_called_with(60)
        assert "3 minutes" in result

    @patch("pryces.presentation.console.commands.monitor_stocks.time.sleep")
    @patch("pryces.presentation.console.commands.monitor_stocks.time.monotonic")
    def test_execute_accumulates_notifications_across_cycles(self, mock_monotonic, mock_sleep):
        crossing_fifty = create_stock_crossing_fifty_day("AAPL")
        crossing_two_hundred = create_stock_crossing_two_hundred_day("AAPL")
        no_crossing = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.side_effect = [
            [crossing_fifty],
            [no_crossing],
            [crossing_two_hundred],
        ]
        # 3 cycles over 3 minutes: start(0), check(60<180), check(120<180), check(180>=180)
        mock_monotonic.side_effect = [0, 60, 120, 180]

        result = self.command.execute(symbols="AAPL", interval="60", duration="3")

        assert "1 stocks checked" in result
        assert "3 minutes" in result

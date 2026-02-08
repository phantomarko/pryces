from decimal import Decimal
from unittest.mock import Mock

from pryces.application.dtos import StockPriceDTO
from pryces.application.interfaces import MessageSender, StockProvider
from pryces.application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
    TriggerType,
)
from tests.fixtures.factories import (
    create_stock_crossing_both_averages,
    create_stock_crossing_fifty_day,
    create_stock_crossing_two_hundred_day,
    create_stock_no_crossing,
)


class TestTriggerStocksNotifications:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockProvider)
        self.mock_sender = Mock(spec=MessageSender)
        self.use_case = TriggerStocksNotifications(
            provider=self.mock_provider, sender=self.mock_sender
        )

    def test_handle_sends_milestone_notification_for_fifty_day_crossing(self):
        stock = create_stock_crossing_fifty_day("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["AAPL"])

        self.use_case.handle(request)

        self.mock_sender.send_message.assert_called_once()
        message = self.mock_sender.send_message.call_args[0][0]
        assert "AAPL" in message
        assert "50-day" in message

    def test_handle_sends_milestone_notification_for_two_hundred_day_crossing(self):
        stock = create_stock_crossing_two_hundred_day("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["GOOGL"])

        self.use_case.handle(request)

        self.mock_sender.send_message.assert_called_once()
        message = self.mock_sender.send_message.call_args[0][0]
        assert "GOOGL" in message
        assert "200-day" in message

    def test_handle_sends_both_notifications_when_both_averages_crossed(self):
        stock = create_stock_crossing_both_averages("MSFT")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["MSFT"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 2
        messages = [c[0][0] for c in self.mock_sender.send_message.call_args_list]
        assert any("50-day" in m for m in messages)
        assert any("200-day" in m for m in messages)

    def test_handle_does_not_send_when_no_crossings(self):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["AAPL"])

        self.use_case.handle(request)

        self.mock_sender.send_message.assert_not_called()

    def test_handle_sends_notifications_only_for_stocks_with_crossings(self):
        crossing_stock = create_stock_crossing_fifty_day("AAPL")
        non_crossing_stock = create_stock_no_crossing("GOOGL")
        self.mock_provider.get_stocks.return_value = [crossing_stock, non_crossing_stock]
        request = TriggerStocksNotificationsRequest(
            type=TriggerType.MILESTONES, symbols=["AAPL", "GOOGL"]
        )

        self.use_case.handle(request)

        self.mock_sender.send_message.assert_called_once()
        message = self.mock_sender.send_message.call_args[0][0]
        assert "AAPL" in message

    def test_handle_sends_notifications_for_multiple_stocks_with_crossings(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_two_hundred_day("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock1, stock2]
        request = TriggerStocksNotificationsRequest(
            type=TriggerType.MILESTONES, symbols=["AAPL", "GOOGL"]
        )

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 2
        messages = [c[0][0] for c in self.mock_sender.send_message.call_args_list]
        assert any("AAPL" in m for m in messages)
        assert any("GOOGL" in m for m in messages)

    def test_handle_returns_dtos_for_all_stocks(self):
        stocks = [
            create_stock_crossing_fifty_day("AAPL"),
            create_stock_no_crossing("GOOGL"),
        ]
        self.mock_provider.get_stocks.return_value = stocks
        request = TriggerStocksNotificationsRequest(
            type=TriggerType.MILESTONES, symbols=["AAPL", "GOOGL"]
        )

        result = self.use_case.handle(request)

        assert len(result) == 2
        assert all(isinstance(r, StockPriceDTO) for r in result)
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "GOOGL"
        assert len(result[0].notifications) == 1
        assert "50-day" in result[0].notifications[0]
        assert result[1].notifications == []

    def test_handle_returns_empty_list_for_empty_symbols(self):
        self.mock_provider.get_stocks.return_value = []
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=[])

        result = self.use_case.handle(request)

        assert result == []
        self.mock_sender.send_message.assert_not_called()
        self.mock_provider.get_stocks.assert_called_once_with([])

    def test_handle_calls_provider_with_correct_symbols(self):
        self.mock_provider.get_stocks.return_value = []
        request = TriggerStocksNotificationsRequest(
            type=TriggerType.MILESTONES, symbols=["AAPL", "GOOGL", "MSFT"]
        )

        self.use_case.handle(request)

        self.mock_provider.get_stocks.assert_called_once_with(["AAPL", "GOOGL", "MSFT"])

    def test_handle_returns_dtos_with_correct_prices(self):
        stock = create_stock_crossing_fifty_day("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["AAPL"])

        result = self.use_case.handle(request)

        assert result[0].currentPrice == Decimal("101")
        assert result[0].symbol == "AAPL"
        assert len(result[0].notifications) == 1
        assert "50-day" in result[0].notifications[0]

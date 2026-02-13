from unittest.mock import Mock

from pryces.application.interfaces import MessageSender, StockProvider
from pryces.application.services import NotificationService
from pryces.application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
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
        self.notification_service = NotificationService(self.mock_sender)
        self.use_case = TriggerStocksNotifications(
            provider=self.mock_provider, notification_service=self.notification_service
        )

    def test_handle_sends_milestone_notification_for_fifty_day_crossing(self):
        stock = create_stock_crossing_fifty_day("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 2

    def test_handle_sends_milestone_notification_for_two_hundred_day_crossing(self):
        stock = create_stock_crossing_two_hundred_day("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["GOOGL"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 2

    def test_handle_sends_both_notifications_when_both_averages_crossed(self):
        stock = create_stock_crossing_both_averages("MSFT")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["MSFT"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 3

    def test_handle_sends_market_open_even_when_no_crossings(self):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        self.use_case.handle(request)

        self.mock_sender.send_message.assert_called_once()

    def test_handle_sends_notifications_for_all_stocks_with_market_open(self):
        crossing_stock = create_stock_crossing_fifty_day("AAPL")
        non_crossing_stock = create_stock_no_crossing("GOOGL")
        self.mock_provider.get_stocks.return_value = [crossing_stock, non_crossing_stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL", "GOOGL"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 3

    def test_handle_sends_notifications_for_multiple_stocks_with_crossings(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_two_hundred_day("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock1, stock2]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL", "GOOGL"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 4

    def test_handle_does_nothing_for_empty_symbols(self):
        self.mock_provider.get_stocks.return_value = []
        request = TriggerStocksNotificationsRequest(symbols=[])

        self.use_case.handle(request)

        self.mock_sender.send_message.assert_not_called()
        self.mock_provider.get_stocks.assert_called_once_with([])

    def test_handle_calls_provider_with_correct_symbols(self):
        self.mock_provider.get_stocks.return_value = []
        request = TriggerStocksNotificationsRequest(symbols=["AAPL", "GOOGL", "MSFT"])

        self.use_case.handle(request)

        self.mock_provider.get_stocks.assert_called_once_with(["AAPL", "GOOGL", "MSFT"])

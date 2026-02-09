from unittest.mock import Mock

from pryces.application.dtos import NotificationDTO
from pryces.application.interfaces import MessageSender, StockProvider
from pryces.application.services import NotificationService
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
        self.notification_service = NotificationService(self.mock_sender)
        self.use_case = TriggerStocksNotifications(
            provider=self.mock_provider, notification_service=self.notification_service
        )

    def test_handle_sends_milestone_notification_for_fifty_day_crossing(self):
        stock = create_stock_crossing_fifty_day("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["AAPL"])

        result = self.use_case.handle(request)

        assert len(result) == 1
        assert "AAPL" in result[0].message
        assert "50-day" in result[0].message
        self.mock_sender.send_message.assert_called_once()

    def test_handle_sends_milestone_notification_for_two_hundred_day_crossing(self):
        stock = create_stock_crossing_two_hundred_day("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["GOOGL"])

        result = self.use_case.handle(request)

        assert len(result) == 1
        assert "GOOGL" in result[0].message
        assert "200-day" in result[0].message
        self.mock_sender.send_message.assert_called_once()

    def test_handle_sends_both_notifications_when_both_averages_crossed(self):
        stock = create_stock_crossing_both_averages("MSFT")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["MSFT"])

        result = self.use_case.handle(request)

        assert len(result) == 2
        messages = [r.message for r in result]
        assert any("50-day" in m for m in messages)
        assert any("200-day" in m for m in messages)

    def test_handle_does_not_send_when_no_crossings(self):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["AAPL"])

        result = self.use_case.handle(request)

        assert result == []
        self.mock_sender.send_message.assert_not_called()

    def test_handle_sends_notifications_only_for_stocks_with_crossings(self):
        crossing_stock = create_stock_crossing_fifty_day("AAPL")
        non_crossing_stock = create_stock_no_crossing("GOOGL")
        self.mock_provider.get_stocks.return_value = [crossing_stock, non_crossing_stock]
        request = TriggerStocksNotificationsRequest(
            type=TriggerType.MILESTONES, symbols=["AAPL", "GOOGL"]
        )

        result = self.use_case.handle(request)

        assert len(result) == 1
        assert "AAPL" in result[0].message
        self.mock_sender.send_message.assert_called_once()

    def test_handle_sends_notifications_for_multiple_stocks_with_crossings(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_two_hundred_day("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock1, stock2]
        request = TriggerStocksNotificationsRequest(
            type=TriggerType.MILESTONES, symbols=["AAPL", "GOOGL"]
        )

        result = self.use_case.handle(request)

        assert len(result) == 2
        messages = [r.message for r in result]
        assert any("AAPL" in m for m in messages)
        assert any("GOOGL" in m for m in messages)
        assert self.mock_sender.send_message.call_count == 2

    def test_handle_returns_notification_dtos(self):
        stock = create_stock_crossing_fifty_day("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["AAPL"])

        result = self.use_case.handle(request)

        assert len(result) == 1
        assert all(isinstance(r, NotificationDTO) for r in result)
        assert "50-day" in result[0].message

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

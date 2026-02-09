from unittest.mock import Mock

from pryces.application.dtos import NotificationDTO
from pryces.application.interfaces import StockProvider
from pryces.application.services import NotificationService
from pryces.application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
    TriggerType,
)
from pryces.domain.notifications import Notification
from tests.fixtures.factories import (
    create_stock_crossing_both_averages,
    create_stock_crossing_fifty_day,
    create_stock_crossing_two_hundred_day,
    create_stock_no_crossing,
)


class TestTriggerStocksNotifications:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockProvider)
        self.mock_notification_service = Mock(spec=NotificationService)
        self.use_case = TriggerStocksNotifications(
            provider=self.mock_provider, notification_service=self.mock_notification_service
        )

    def _setup_notifications_return(self, stock):
        stock.generate_milestones_notifications()
        self.mock_notification_service.send_stock_notifications.return_value = list(
            stock.notifications
        )

    def test_handle_sends_milestone_notification_for_fifty_day_crossing(self):
        stock = create_stock_crossing_fifty_day("AAPL")
        self._setup_notifications_return(stock)
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["AAPL"])

        result = self.use_case.handle(request)

        self.mock_notification_service.send_stock_notifications.assert_called_once()
        assert len(result) == 1
        assert "AAPL" in result[0].message
        assert "50-day" in result[0].message

    def test_handle_sends_milestone_notification_for_two_hundred_day_crossing(self):
        stock = create_stock_crossing_two_hundred_day("GOOGL")
        self._setup_notifications_return(stock)
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["GOOGL"])

        result = self.use_case.handle(request)

        self.mock_notification_service.send_stock_notifications.assert_called_once()
        assert len(result) == 1
        assert "GOOGL" in result[0].message
        assert "200-day" in result[0].message

    def test_handle_sends_both_notifications_when_both_averages_crossed(self):
        stock = create_stock_crossing_both_averages("MSFT")
        self._setup_notifications_return(stock)
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["MSFT"])

        result = self.use_case.handle(request)

        assert len(result) == 2
        messages = [r.message for r in result]
        assert any("50-day" in m for m in messages)
        assert any("200-day" in m for m in messages)

    def test_handle_does_not_send_when_no_crossings(self):
        stock = create_stock_no_crossing("AAPL")
        self.mock_notification_service.send_stock_notifications.return_value = []
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(type=TriggerType.MILESTONES, symbols=["AAPL"])

        result = self.use_case.handle(request)

        assert result == []

    def test_handle_sends_notifications_only_for_stocks_with_crossings(self):
        crossing_stock = create_stock_crossing_fifty_day("AAPL")
        crossing_stock.generate_milestones_notifications()
        non_crossing_stock = create_stock_no_crossing("GOOGL")
        self.mock_provider.get_stocks.return_value = [crossing_stock, non_crossing_stock]

        self.mock_notification_service.send_stock_notifications.side_effect = [
            list(crossing_stock.notifications),
            [],
        ]

        request = TriggerStocksNotificationsRequest(
            type=TriggerType.MILESTONES, symbols=["AAPL", "GOOGL"]
        )

        result = self.use_case.handle(request)

        assert len(result) == 1
        assert "AAPL" in result[0].message

    def test_handle_sends_notifications_for_multiple_stocks_with_crossings(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock1.generate_milestones_notifications()
        stock2 = create_stock_crossing_two_hundred_day("GOOGL")
        stock2.generate_milestones_notifications()
        self.mock_provider.get_stocks.return_value = [stock1, stock2]

        self.mock_notification_service.send_stock_notifications.side_effect = [
            list(stock1.notifications),
            list(stock2.notifications),
        ]

        request = TriggerStocksNotificationsRequest(
            type=TriggerType.MILESTONES, symbols=["AAPL", "GOOGL"]
        )

        result = self.use_case.handle(request)

        assert len(result) == 2
        messages = [r.message for r in result]
        assert any("AAPL" in m for m in messages)
        assert any("GOOGL" in m for m in messages)

    def test_handle_returns_notification_dtos(self):
        stock = create_stock_crossing_fifty_day("AAPL")
        self._setup_notifications_return(stock)
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
        self.mock_notification_service.send_stock_notifications.assert_not_called()
        self.mock_provider.get_stocks.assert_called_once_with([])

    def test_handle_calls_provider_with_correct_symbols(self):
        self.mock_provider.get_stocks.return_value = []
        request = TriggerStocksNotificationsRequest(
            type=TriggerType.MILESTONES, symbols=["AAPL", "GOOGL", "MSFT"]
        )

        self.use_case.handle(request)

        self.mock_provider.get_stocks.assert_called_once_with(["AAPL", "GOOGL", "MSFT"])

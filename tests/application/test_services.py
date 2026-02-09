from unittest.mock import Mock

from pryces.application.interfaces import MessageSender
from pryces.application.services import NotificationService
from tests.fixtures.factories import (
    create_stock_crossing_both_averages,
    create_stock_crossing_fifty_day,
    create_stock_crossing_two_hundred_day,
    create_stock_no_crossing,
)


class TestNotificationService:

    def setup_method(self):
        self.mock_sender = Mock(spec=MessageSender)
        self.service = NotificationService(self.mock_sender)

    def test_sends_notifications_via_message_sender(self):
        stock = create_stock_crossing_fifty_day("AAPL")

        self.service.send_stock_milestones_notifications(stock)

        assert self.mock_sender.send_message.call_count == 2
        messages = [call[0][0] for call in self.mock_sender.send_message.call_args_list]
        assert all("AAPL" in m for m in messages)

    def test_returns_sent_notifications(self):
        stock = create_stock_crossing_fifty_day("AAPL")

        result = self.service.send_stock_milestones_notifications(stock)

        assert len(result) == 2
        assert result[0] is stock.notifications[0]
        assert result[1] is stock.notifications[1]

    def test_adds_sent_notifications_to_dictionary(self):
        stock = create_stock_crossing_fifty_day("AAPL")

        self.service.send_stock_milestones_notifications(stock)

        assert "AAPL" in self.service.notifications_sent
        assert len(self.service.notifications_sent["AAPL"]) == 2

    def test_skips_duplicate_notifications_for_same_symbol(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_fifty_day("AAPL")

        self.service.send_stock_milestones_notifications(stock1)
        result = self.service.send_stock_milestones_notifications(stock2)

        assert self.mock_sender.send_message.call_count == 2
        assert len(self.service.notifications_sent["AAPL"]) == 2
        assert result == []

    def test_handles_multiple_stocks_independently(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_fifty_day("GOOGL")

        result1 = self.service.send_stock_milestones_notifications(stock1)
        result2 = self.service.send_stock_milestones_notifications(stock2)

        assert self.mock_sender.send_message.call_count == 4
        assert "AAPL" in self.service.notifications_sent
        assert "GOOGL" in self.service.notifications_sent
        assert len(result1) == 2
        assert len(result2) == 2

    def test_handles_stock_with_no_crossing_notifications(self):
        stock = create_stock_no_crossing("AAPL")

        result = self.service.send_stock_milestones_notifications(stock)

        self.mock_sender.send_message.assert_called_once()
        assert "AAPL" in self.service.notifications_sent
        assert len(result) == 1

    def test_sends_unsent_notification_type_even_if_other_type_already_sent(self):
        stock_fifty = create_stock_crossing_fifty_day("AAPL")
        result1 = self.service.send_stock_milestones_notifications(stock_fifty)

        stock_both = create_stock_crossing_both_averages("AAPL")
        result2 = self.service.send_stock_milestones_notifications(stock_both)

        assert self.mock_sender.send_message.call_count == 3
        assert len(self.service.notifications_sent["AAPL"]) == 3
        assert len(result1) == 2
        assert len(result2) == 1

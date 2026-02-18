from decimal import Decimal
from unittest.mock import Mock

from pryces.application.interfaces import MessageSender
from pryces.application.services import NotificationService
from pryces.domain.notifications import NotificationType
from pryces.domain.stocks import MarketState, Stock
from pryces.infrastructure.implementations import InMemoryNotificationRepository
from tests.fixtures.factories import (
    create_stock_crossing_both_averages,
    create_stock_crossing_fifty_day,
    create_stock_crossing_two_hundred_day,
    create_stock_no_crossing,
)


class TestNotificationService:

    def setup_method(self):
        self.mock_sender = Mock(spec=MessageSender)
        self.repo = InMemoryNotificationRepository()
        self.service = NotificationService(self.mock_sender, self.repo)

    def test_sends_notifications_via_message_sender(self):
        stock = create_stock_crossing_fifty_day("AAPL")

        self.service.send_stock_notifications(stock, None)

        assert self.mock_sender.send_message.call_count == 2
        messages = [call[0][0] for call in self.mock_sender.send_message.call_args_list]
        assert all("AAPL" in m for m in messages)

    def test_returns_sent_notifications(self):
        stock = create_stock_crossing_fifty_day("AAPL")

        result = self.service.send_stock_notifications(stock, None)

        assert len(result) == 2
        assert result[0] is stock.notifications[0]
        assert result[1] is stock.notifications[1]

    def test_saves_sent_notifications_to_repository(self):
        stock = create_stock_crossing_fifty_day("AAPL")

        self.service.send_stock_notifications(stock, None)

        for notification in stock.notifications:
            assert self.repo.exists_by_type("AAPL", notification.type)

    def test_skips_duplicate_notifications_for_same_symbol(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_fifty_day("AAPL")

        self.service.send_stock_notifications(stock1, None)
        result = self.service.send_stock_notifications(stock2, None)

        assert self.mock_sender.send_message.call_count == 2
        assert result == []

    def test_handles_multiple_stocks_independently(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_fifty_day("GOOGL")

        result1 = self.service.send_stock_notifications(stock1, None)
        result2 = self.service.send_stock_notifications(stock2, None)

        assert self.mock_sender.send_message.call_count == 4
        for notification in stock1.notifications:
            assert self.repo.exists_by_type("AAPL", notification.type)
        for notification in stock2.notifications:
            assert self.repo.exists_by_type("GOOGL", notification.type)
        assert len(result1) == 2
        assert len(result2) == 2

    def test_handles_stock_with_no_crossing_notifications(self):
        stock = create_stock_no_crossing("AAPL")

        result = self.service.send_stock_notifications(stock, None)

        self.mock_sender.send_message.assert_called_once()
        assert self.repo.exists_by_type("AAPL", NotificationType.REGULAR_MARKET_OPEN)
        assert len(result) == 1

    def test_sends_unsent_notification_type_even_if_other_type_already_sent(self):
        stock_fifty = create_stock_crossing_fifty_day("AAPL")
        result1 = self.service.send_stock_notifications(stock_fifty, None)

        stock_both = create_stock_crossing_both_averages("AAPL")
        result2 = self.service.send_stock_notifications(stock_both, None)

        assert self.mock_sender.send_message.call_count == 3
        assert self.repo.exists_by_type("AAPL", NotificationType.REGULAR_MARKET_OPEN)
        assert self.repo.exists_by_type("AAPL", NotificationType.SMA50_CROSSED)
        assert self.repo.exists_by_type("AAPL", NotificationType.SMA200_CROSSED)
        assert len(result1) == 2
        assert len(result2) == 1

    def test_sends_new_52_week_high_notification_when_past_stock_provided(self):
        stock = Stock(
            symbol="AAPL",
            currentPrice=Decimal("200.00"),
            openPrice=Decimal("195.00"),
            previousClosePrice=Decimal("190.00"),
            marketState=MarketState.OPEN,
        )
        past_stock = Stock(
            symbol="AAPL", currentPrice=Decimal("180.00"), fiftyTwoWeekHigh=Decimal("190.00")
        )

        result = self.service.send_stock_notifications(stock, past_stock)

        types = {n.type for n in result}
        assert NotificationType.NEW_52_WEEK_HIGH in types

    def test_sends_new_52_week_low_notification_when_past_stock_provided(self):
        stock = Stock(
            symbol="AAPL",
            currentPrice=Decimal("100.00"),
            openPrice=Decimal("105.00"),
            previousClosePrice=Decimal("110.00"),
            marketState=MarketState.OPEN,
        )
        past_stock = Stock(
            symbol="AAPL", currentPrice=Decimal("120.00"), fiftyTwoWeekLow=Decimal("110.00")
        )

        result = self.service.send_stock_notifications(stock, past_stock)

        types = {n.type for n in result}
        assert NotificationType.NEW_52_WEEK_LOW in types

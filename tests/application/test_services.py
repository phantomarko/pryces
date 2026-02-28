from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from pryces.application.senders import MessageSender
from pryces.application.services import NotificationService
from pryces.domain.notifications import NotificationType
from pryces.domain.stocks import MarketState, Stock
from pryces.domain.target_prices import TargetPrice
from pryces.infrastructure.repositories import (
    InMemoryMarketTransitionRepository,
    InMemoryNotificationRepository,
)
from tests.fixtures.factories import (
    create_stock,
    create_stock_crossing_both_averages,
    create_stock_crossing_fifty_day,
    create_stock_crossing_two_hundred_day,
    create_stock_no_crossing,
)


class TestNotificationService:

    def setup_method(self):
        self.mock_sender = Mock(spec=MessageSender)
        self.repo = InMemoryNotificationRepository()
        self.transition_repo = InMemoryMarketTransitionRepository()
        self.clock = Mock(return_value=datetime(2024, 1, 1, 9, 0, 0))
        self.service = NotificationService(
            self.mock_sender, self.repo, self.transition_repo, self.clock
        )

    def test_sends_notifications_via_message_sender(self):
        stock = create_stock_crossing_fifty_day("AAPL")

        self.service.send_stock_notifications(stock)

        assert self.mock_sender.send_message.call_count == 2
        messages = [call[0][0] for call in self.mock_sender.send_message.call_args_list]
        assert all("AAPL" in m for m in messages)

    def test_saves_sent_notifications_to_repository(self):
        stock = create_stock_crossing_fifty_day("AAPL")

        self.service.send_stock_notifications(stock)

        for notification in stock.notifications:
            assert self.repo.exists_by_type("AAPL", notification.type)

    def test_skips_duplicate_notifications_for_same_symbol(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_fifty_day("AAPL")

        self.service.send_stock_notifications(stock1)
        self.service.send_stock_notifications(stock2)

        assert self.mock_sender.send_message.call_count == 2

    def test_handles_multiple_stocks_independently(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_fifty_day("GOOGL")

        self.service.send_stock_notifications(stock1)
        self.service.send_stock_notifications(stock2)

        assert self.mock_sender.send_message.call_count == 4
        for notification in stock1.notifications:
            assert self.repo.exists_by_type("AAPL", notification.type)
        for notification in stock2.notifications:
            assert self.repo.exists_by_type("GOOGL", notification.type)

    def test_handles_stock_with_no_crossing_notifications(self):
        stock = create_stock_no_crossing("AAPL")

        self.service.send_stock_notifications(stock)

        self.mock_sender.send_message.assert_called_once()
        assert self.repo.exists_by_type("AAPL", NotificationType.REGULAR_MARKET_OPEN)

    def test_sends_unsent_notification_type_even_if_other_type_already_sent(self):
        stock_fifty = create_stock_crossing_fifty_day("AAPL")
        self.service.send_stock_notifications(stock_fifty)

        stock_both = create_stock_crossing_both_averages("AAPL")
        self.service.send_stock_notifications(stock_both)

        assert self.mock_sender.send_message.call_count == 3
        assert self.repo.exists_by_type("AAPL", NotificationType.REGULAR_MARKET_OPEN)
        assert self.repo.exists_by_type("AAPL", NotificationType.SMA50_CROSSED)
        assert self.repo.exists_by_type("AAPL", NotificationType.SMA200_CROSSED)

    def test_sends_new_52_week_high_notification_when_snapshot_exists(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("180.00"),
            fifty_two_week_high=Decimal("190.00"),
            market_state=MarketState.OPEN,
        )
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            open_price=Decimal("195.00"),
            previous_close_price=Decimal("190.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        self.service.send_stock_notifications(stock)

        assert self.repo.exists_by_type("AAPL", NotificationType.NEW_52_WEEK_HIGH)

    def test_sends_new_52_week_low_notification_when_snapshot_exists(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("120.00"),
            fifty_two_week_low=Decimal("110.00"),
            market_state=MarketState.OPEN,
        )
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            open_price=Decimal("105.00"),
            previous_close_price=Decimal("110.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        self.service.send_stock_notifications(stock)

        assert self.repo.exists_by_type("AAPL", NotificationType.NEW_52_WEEK_LOW)

    def test_no_delay_when_price_delay_is_none(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("145.00"),
            market_state=MarketState.PRE,
            price_delay_in_minutes=None,
        )
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=None,
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )
        stock.update(source)

        self.service.send_stock_notifications(stock)

        self.mock_sender.send_message.assert_called()

    def test_no_delay_when_price_delay_is_zero(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("145.00"),
            market_state=MarketState.PRE,
            price_delay_in_minutes=0,
        )
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=0,
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )
        stock.update(source)

        self.service.send_stock_notifications(stock)

        self.mock_sender.send_message.assert_called()

    def test_suppresses_notifications_on_transition_cycle_when_delay_positive(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("145.00"),
            market_state=MarketState.PRE,
            price_delay_in_minutes=15,
        )
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
        )
        stock.update(source)

        self.service.send_stock_notifications(stock)

        self.mock_sender.send_message.assert_not_called()

    def test_suppresses_notifications_during_delay_window(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("145.00"),
            market_state=MarketState.PRE,
            price_delay_in_minutes=15,
        )
        source_transition = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
        )
        stock.update(source_transition)
        self.service.send_stock_notifications(stock)

        source_same = Stock(
            symbol="AAPL",
            current_price=Decimal("151.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
        )
        stock.update(source_same)
        self.clock.return_value = datetime(2024, 1, 1, 9, 5, 0)
        self.service.send_stock_notifications(stock)

        self.mock_sender.send_message.assert_not_called()

    def test_fires_notifications_after_delay_elapsed(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("145.00"),
            market_state=MarketState.PRE,
            price_delay_in_minutes=15,
        )
        source_transition = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
        )
        stock.update(source_transition)
        self.service.send_stock_notifications(stock)

        source_same = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )
        stock.update(source_same)
        self.clock.return_value = datetime(2024, 1, 1, 9, 16, 0)
        self.service.send_stock_notifications(stock)

        self.mock_sender.send_message.assert_called()

    def test_no_delay_suppression_when_no_snapshot(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )

        self.service.send_stock_notifications(stock)

        self.mock_sender.send_message.assert_called()

    def test_non_open_post_transitions_not_treated_as_delay_triggers(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
        )
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.PRE,
            price_delay_in_minutes=15,
        )
        stock.update(source)

        self.service.send_stock_notifications(stock)

        assert self.transition_repo.get("AAPL") is None


class TestSendStockTargetsNotifications:

    def setup_method(self):
        self.mock_sender = Mock(spec=MessageSender)
        self.repo = InMemoryNotificationRepository()
        self.transition_repo = InMemoryMarketTransitionRepository()
        self.clock = Mock(return_value=datetime(2024, 1, 1, 9, 0, 0))
        self.service = NotificationService(
            self.mock_sender, self.repo, self.transition_repo, self.clock
        )

    def test_returns_empty_list_when_no_targets(self):
        stock = create_stock("AAPL", Decimal("150.00"))

        result = self.service.send_stock_targets_notifications(stock, [])

        assert result == []
        self.mock_sender.send_message.assert_not_called()

    def test_returns_empty_list_when_no_target_is_reached(self):
        # entry=100, target=200, current=150 — target not reached
        target = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        target.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        stock = create_stock("AAPL", Decimal("150.00"))

        result = self.service.send_stock_targets_notifications(stock, [target])

        assert result == []
        self.mock_sender.send_message.assert_not_called()

    def test_returns_triggered_target_and_sends_message_when_target_reached(self):
        # entry=100, target=200, current=200 — target reached
        target = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        target.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        stock = create_stock("AAPL", Decimal("200.00"))

        result = self.service.send_stock_targets_notifications(stock, [target])

        assert result == [target]
        self.mock_sender.send_message.assert_called_once()

    def test_returns_all_triggered_targets_when_multiple_reach_price(self):
        # Two targets both reached
        target1 = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        target1.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        target2 = TargetPrice(symbol="AAPL", target=Decimal("250.00"))
        target2.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        stock = create_stock("AAPL", Decimal("300.00"))

        result = self.service.send_stock_targets_notifications(stock, [target1, target2])

        assert result == [target1, target2]
        assert self.mock_sender.send_message.call_count == 2

    def test_returns_only_triggered_targets_in_mixed_scenario(self):
        # target1 reached, target2 not
        target1 = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        target1.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        target2 = TargetPrice(symbol="AAPL", target=Decimal("500.00"))
        target2.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        stock = create_stock("AAPL", Decimal("250.00"))

        result = self.service.send_stock_targets_notifications(stock, [target1, target2])

        assert result == [target1]
        self.mock_sender.send_message.assert_called_once()

    def test_returns_empty_list_when_target_has_no_entry_price(self):
        # entry not set — generate_notification returns None
        target = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        stock = create_stock("AAPL", Decimal("200.00"))

        result = self.service.send_stock_targets_notifications(stock, [target])

        assert result == []
        self.mock_sender.send_message.assert_not_called()

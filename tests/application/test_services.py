from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from pryces.application.interfaces import MessageSender, StockProvider
from pryces.application.services import NotificationService, StockSynchronizer
from pryces.domain.stocks import MarketState, Stock
from pryces.infrastructure.repositories import (
    InMemoryMarketTransitionRepository,
    InMemoryStockRepository,
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
        self.transition_repo = InMemoryMarketTransitionRepository()
        self.clock = Mock(return_value=datetime(2024, 1, 1, 9, 0, 0))
        self.service = NotificationService(self.mock_sender, self.transition_repo, self.clock)

    def test_sends_notifications_via_message_sender(self):
        stock = create_stock_crossing_fifty_day("AAPL")

        self.service.send_stock_notifications(stock)

        assert self.mock_sender.send_message.call_count == 2
        messages = [call[0][0] for call in self.mock_sender.send_message.call_args_list]
        assert all("AAPL" in m for m in messages)

    def test_handles_multiple_stocks_independently(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_fifty_day("GOOGL")

        self.service.send_stock_notifications(stock1)
        self.service.send_stock_notifications(stock2)

        assert self.mock_sender.send_message.call_count == 4

    def test_handles_stock_with_no_crossing_notifications(self):
        stock = create_stock_no_crossing("AAPL")

        self.service.send_stock_notifications(stock)

        self.mock_sender.send_message.assert_called_once()

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

        messages = [call[0][0] for call in self.mock_sender.send_message.call_args_list]
        assert any("52-week high" in m for m in messages)

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

        messages = [call[0][0] for call in self.mock_sender.send_message.call_args_list]
        assert any("52-week low" in m for m in messages)

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

    def test_sends_target_notification_when_target_reached(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.sync_targets([Decimal("200.00")])
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        self.service.send_stock_notifications(stock)

        self.mock_sender.send_message.assert_called()
        assert stock.targets == []

    def test_does_not_remove_unreached_target(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.sync_targets([Decimal("200.00")])
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        self.service.send_stock_notifications(stock)

        assert len(stock.targets) == 1

    def test_suppresses_target_notifications_during_delay_window(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            market_state=MarketState.PRE,
            price_delay_in_minutes=15,
        )
        stock.sync_targets([Decimal("200.00")])
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
        )
        stock.update(source)

        self.service.send_stock_notifications(stock)

        # Target should still be there since notifications were suppressed
        assert len(stock.targets) == 1
        self.mock_sender.send_message.assert_not_called()


class TestStockSynchronizer:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockProvider)
        self.stock_repository = InMemoryStockRepository()
        self.synchronizer = StockSynchronizer(
            provider=self.mock_provider,
            stock_repository=self.stock_repository,
        )

    def test_fetch_and_sync_returns_fresh_stock_when_no_existing(self):
        stock = create_stock("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]

        result = self.synchronizer.fetch_and_sync(["AAPL"], {})

        assert result == [stock]

    def test_fetch_and_sync_merges_with_existing_stock(self):
        existing = Stock(
            symbol="AAPL",
            current_price=Decimal("180.00"),
            fifty_two_week_high=Decimal("190.00"),
        )
        self.stock_repository.save_batch([existing])
        fresh = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            market_state=MarketState.OPEN,
        )
        self.mock_provider.get_stocks.return_value = [fresh]

        result = self.synchronizer.fetch_and_sync(["AAPL"], {})

        assert result == [existing]
        assert existing.current_price == Decimal("200.00")
        assert existing.snapshot is not None

    def test_fetch_and_sync_syncs_target_prices(self):
        stock = create_stock("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]

        result = self.synchronizer.fetch_and_sync(["AAPL"], {"AAPL": [Decimal("200.00")]})

        assert len(result[0].targets) == 1
        assert result[0].targets[0].target == Decimal("200.00")

    def test_fetch_and_sync_with_empty_symbols_returns_empty(self):
        self.mock_provider.get_stocks.return_value = []

        result = self.synchronizer.fetch_and_sync([], {})

        assert result == []

    def test_persist_saves_stocks_to_repository(self):
        stock = create_stock("AAPL")

        self.synchronizer.persist([stock])

        assert self.stock_repository.get("AAPL") is stock

from decimal import Decimal

from pryces.infrastructure.formatters import ConsolidatingNotificationFormatter
from pryces.domain.stocks import MarketState, Stock
from tests.fixtures.factories import (
    _DEFAULT_NOW,
    generate_and_drain,
    make_stock,
    open_stock_after_burn,
    open_stock_ready_for_target,
)

_formatter = ConsolidatingNotificationFormatter()


class TestTargetPriceNotifications:
    def test_generate_notifications_appends_target_price_reached_when_target_is_reached(self):
        stock = open_stock_ready_for_target("100.00", "200.00", "200.00")
        messages = generate_and_drain(stock)
        assert any("hit target" in m for m in messages)

    def test_generate_notifications_removes_triggered_targets_from_stock(self):
        stock = open_stock_ready_for_target("100.00", "200.00", "200.00")
        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)
        assert result.fulfilled_targets == [Decimal("200.00")]

    def test_generate_notifications_does_not_include_unreached_target(self):
        stock = make_stock(current_price="100.00", previous_close_price="148.00")
        stock.sync_targets([Decimal("200.00")])
        source = make_stock(current_price="150.00", previous_close_price="148.00")
        stock.update(source)
        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)
        assert not any("hit target" in m for m in result.messages)
        assert result.fulfilled_targets == []

    def test_generate_notifications_target_notification_message_contains_symbol_and_target(self):
        stock = open_stock_ready_for_target("100.00", "200.00", "200.00")
        messages = generate_and_drain(stock)
        target_messages = [m for m in messages if "hit target" in m]
        assert len(target_messages) == 1
        assert "AAPL" in target_messages[0]
        assert "200.00" in target_messages[0]

    def test_generate_notifications_ignores_targets_when_market_is_post(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="195.00", market_state=MarketState.POST
        )
        stock.sync_targets([Decimal("200.00")])
        source = make_stock(
            current_price="200.00", previous_close_price="195.00", market_state=MarketState.POST
        )
        stock.update(source)
        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)
        assert not any("hit target" in m for m in result.messages)
        assert result.fulfilled_targets == []

    def test_generate_notifications_removes_multiple_triggered_targets(self):
        stock = open_stock_after_burn(current_price="100.00", previous_close_price="295.00")
        stock.sync_targets([Decimal("200.00"), Decimal("250.00")])
        source = make_stock(current_price="300.00", previous_close_price="295.00")
        stock.update(source)
        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)
        target_messages = [m for m in result.messages if "hit target" in m]
        assert len(target_messages) == 2
        assert set(result.fulfilled_targets) == {Decimal("200.00"), Decimal("250.00")}

    def test_generate_notifications_target_price_reached_is_never_deduplicated(self):
        stock = open_stock_after_burn(current_price="100.00", previous_close_price="195.00")
        stock.sync_targets([Decimal("200.00")])
        source1 = make_stock(current_price="200.00", previous_close_price="195.00")
        stock.update(source1)
        result1 = stock.generate_notifications(_DEFAULT_NOW, _formatter)
        assert any("hit target" in m for m in result1.messages)

        stock.sync_targets([Decimal("250.00")])
        source2 = make_stock(current_price="250.00", previous_close_price="195.00")
        stock.update(source2)
        result2 = stock.generate_notifications(_DEFAULT_NOW, _formatter)
        assert any("hit target" in m for m in result2.messages)


class TestSyncTargets:
    def test_sync_targets_sets_entry_price(self):
        stock = make_stock(current_price="150.00")
        stock.sync_targets([Decimal("200.00")])

        source_below = make_stock(current_price="180.00", previous_close_price="148.00")
        stock.update(source_below)
        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)
        assert result.fulfilled_targets == []

        source_hit = make_stock(current_price="200.00", previous_close_price="195.00")
        stock.update(source_hit)
        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)
        assert any("hit target" in m for m in result.messages)

    def test_sync_targets_removes_missing_targets(self):
        stock = make_stock(current_price="150.00")
        stock.generate_notifications(_DEFAULT_NOW, _formatter)
        stock.sync_targets([Decimal("200.00"), Decimal("250.00")])
        stock.sync_targets([Decimal("200.00")])

        source = make_stock(current_price="260.00", previous_close_price="148.00")
        stock.update(source)
        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)

        assert result.fulfilled_targets == [Decimal("200.00")]

    def test_sync_targets_clears_all_on_empty_list(self):
        stock = make_stock(current_price="150.00")
        stock.sync_targets([Decimal("200.00")])
        stock.sync_targets([])

        source = make_stock(current_price="200.00", previous_close_price="148.00")
        stock.update(source)
        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)

        assert result.fulfilled_targets == []

    def test_sync_targets_adds_new_and_preserves_existing(self):
        stock = make_stock(current_price="150.00")
        stock.generate_notifications(_DEFAULT_NOW, _formatter)
        stock.sync_targets([Decimal("200.00")])
        stock.sync_targets([Decimal("200.00"), Decimal("250.00")])

        source = make_stock(current_price="260.00", previous_close_price="148.00")
        stock.update(source)
        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)

        assert set(result.fulfilled_targets) == {Decimal("200.00"), Decimal("250.00")}


class TestFulfilledTargetsInResult:
    def test_generate_notifications_returns_fulfilled_targets(self):
        stock = open_stock_after_burn(current_price="150.00", previous_close_price="145.00")
        stock.sync_targets([Decimal("150.00")])

        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)

        assert len(result.fulfilled_targets) == 1
        assert result.fulfilled_targets[0] == Decimal("150.00")

    def test_generate_notifications_does_not_accumulate_fulfilled_targets_across_calls(self):
        stock = make_stock(current_price="150.00", previous_close_price="145.00")
        stock.sync_targets([Decimal("150.00")])
        stock.generate_notifications(_DEFAULT_NOW, _formatter)

        second_result = stock.generate_notifications(_DEFAULT_NOW, _formatter)

        assert second_result.fulfilled_targets == []

    def test_generate_notifications_returns_empty_fulfilled_when_no_targets_reached(self):
        stock = make_stock(current_price="150.00", previous_close_price="145.00")
        stock.sync_targets([Decimal("200.00")])

        result = stock.generate_notifications(_DEFAULT_NOW, _formatter)

        assert result.fulfilled_targets == []

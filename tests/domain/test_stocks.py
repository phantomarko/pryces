from decimal import Decimal

import pytest

from pryces.domain.stocks import InstrumentType, MarketState, Stock, StockSnapshot
from tests.fixtures.factories import (
    generate_and_drain,
    make_stock,
    open_stock_after_burn,
    open_stock_ready_for_target,
)


class TestStockCreation:
    def test_stock_creation_with_required_fields(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

        assert stock.symbol == "AAPL"
        assert stock.current_price == Decimal("150.00")

    def test_stock_creation_with_all_fields(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            name="Apple Inc.",
            currency="USD",
            previous_close_price=Decimal("149.50"),
            open_price=Decimal("149.75"),
            day_high=Decimal("151.00"),
            day_low=Decimal("149.00"),
            fifty_day_average=Decimal("145.00"),
            two_hundred_day_average=Decimal("140.00"),
            fifty_two_week_high=Decimal("160.00"),
            fifty_two_week_low=Decimal("120.00"),
            kind=InstrumentType.STOCK,
        )

        assert stock.symbol == "AAPL"
        assert stock.current_price == Decimal("150.00")
        assert stock.name == "Apple Inc."
        assert stock.currency == "USD"
        assert stock.previous_close_price == Decimal("149.50")
        assert stock.open_price == Decimal("149.75")
        assert stock.day_high == Decimal("151.00")
        assert stock.day_low == Decimal("149.00")
        assert stock.fifty_day_average == Decimal("145.00")
        assert stock.two_hundred_day_average == Decimal("140.00")
        assert stock.fifty_two_week_high == Decimal("160.00")
        assert stock.fifty_two_week_low == Decimal("120.00")
        assert stock.kind == InstrumentType.STOCK

    def test_stock_is_immutable(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

        try:
            stock.symbol = "GOOGL"
            assert False, "Should not be able to modify frozen dataclass"
        except AttributeError:
            pass

    def test_stock_optional_fields_default_to_none(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

        assert stock.name is None
        assert stock.currency is None
        assert stock.previous_close_price is None
        assert stock.open_price is None
        assert stock.day_high is None
        assert stock.day_low is None
        assert stock.fifty_day_average is None
        assert stock.two_hundred_day_average is None
        assert stock.fifty_two_week_high is None
        assert stock.fifty_two_week_low is None


class TestHasCrossedSMA:
    def test_has_crossed_sma_returns_false_when_fields_are_missing(self):
        stock = make_stock(current_price="150.00")
        messages = generate_and_drain(stock)
        assert not any("crossed SMA50" in m for m in messages)

        stock_with_previous = make_stock(current_price="150.00", previous_close_price="140.00")
        messages = generate_and_drain(stock_with_previous)
        assert not any("crossed SMA50" in m for m in messages)

        stock_with_average = make_stock(current_price="150.00", fifty_day_average="145.00")
        messages = generate_and_drain(stock_with_average)
        assert not any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_above(self):
        stock = open_stock_after_burn(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_below(self):
        stock = open_stock_after_burn(
            current_price="140.00",
            previous_close_price="150.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_returns_false_when_no_crossing(self):
        stock_both_above = make_stock(
            current_price="150.00", previous_close_price="148.00", fifty_day_average="145.00"
        )
        messages = generate_and_drain(stock_both_above)
        assert not any("crossed SMA50" in m for m in messages)

        stock_both_below = make_stock(
            current_price="140.00", previous_close_price="142.00", fifty_day_average="145.00"
        )
        messages = generate_and_drain(stock_both_below)
        assert not any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_above_when_current_equals_average(self):
        stock = open_stock_after_burn(
            current_price="145.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_below_when_current_equals_average(self):
        stock = open_stock_after_burn(
            current_price="145.00",
            previous_close_price="150.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_returns_false_when_previous_equals_average(self):
        stock_current_above = make_stock(
            current_price="150.00", previous_close_price="145.00", fifty_day_average="145.00"
        )
        messages = generate_and_drain(stock_current_above)
        assert not any("crossed SMA50" in m for m in messages)

        stock_current_below = make_stock(
            current_price="140.00", previous_close_price="145.00", fifty_day_average="145.00"
        )
        messages = generate_and_drain(stock_current_below)
        assert not any("crossed SMA50" in m for m in messages)


class TestIsCloseToSMA:
    def test_is_close_to_sma_returns_false_when_fields_are_missing(self):
        stock = make_stock(current_price="150.00")
        messages = generate_and_drain(stock)
        assert not any("SMA50 at" in m for m in messages)

        stock_with_previous = make_stock(current_price="150.00", previous_close_price="140.00")
        messages = generate_and_drain(stock_with_previous)
        assert not any("SMA50 at" in m for m in messages)

        stock_with_average = make_stock(current_price="150.00", fifty_day_average="145.00")
        messages = generate_and_drain(stock_with_average)
        assert not any("SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_true_when_approaching_from_below_within_threshold(
        self, close_to_sma50_from_below_stock
    ):
        messages = generate_and_drain(close_to_sma50_from_below_stock)
        assert any("below SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_true_when_approaching_from_above_within_threshold(
        self, close_to_sma50_from_above_stock
    ):
        messages = generate_and_drain(close_to_sma50_from_above_stock)
        assert any("above SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_false_when_approaching_from_below_beyond_threshold(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="95.00", fifty_day_average="106.00"
        )
        messages = generate_and_drain(stock)
        assert not any("SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_false_when_approaching_from_above_beyond_threshold(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="105.00", fifty_day_average="94.00"
        )
        messages = generate_and_drain(stock)
        assert not any("SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_true_at_exact_threshold_from_below(
        self, close_to_sma50_from_below_stock
    ):
        messages = generate_and_drain(close_to_sma50_from_below_stock)
        assert any("below SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_true_at_exact_threshold_from_above(
        self, close_to_sma50_from_above_stock
    ):
        messages = generate_and_drain(close_to_sma50_from_above_stock)
        assert any("above SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_false_when_previous_close_on_same_side_as_price(self):
        stock_both_above = make_stock(
            current_price="110.00", previous_close_price="108.00", fifty_day_average="100.00"
        )
        messages = generate_and_drain(stock_both_above)
        assert not any("SMA50 at" in m for m in messages)

        stock_both_below = make_stock(
            current_price="90.00", previous_close_price="92.00", fifty_day_average="100.00"
        )
        messages = generate_and_drain(stock_both_below)
        assert not any("SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_false_when_previous_equals_average(self):
        stock_current_above = make_stock(
            current_price="103.00", previous_close_price="100.00", fifty_day_average="100.00"
        )
        messages = generate_and_drain(stock_current_above)
        assert not any("SMA50 at" in m for m in messages)

        stock_current_below = make_stock(
            current_price="97.00", previous_close_price="100.00", fifty_day_average="100.00"
        )
        messages = generate_and_drain(stock_current_below)
        assert not any("SMA50 at" in m for m in messages)


class TestCloseToSMA50Notifications:
    def test_generate_notifications_adds_close_to_sma50_when_approaching_from_below(self):
        stock = open_stock_after_burn(
            current_price="100.00", previous_close_price="95.00", fifty_day_average="102.00"
        )
        messages = generate_and_drain(stock)
        assert any("below SMA50 at" in m for m in messages)

    def test_generate_notifications_adds_close_to_sma50_when_approaching_from_above(self):
        stock = open_stock_after_burn(
            current_price="100.00", previous_close_price="105.00", fifty_day_average="98.00"
        )
        messages = generate_and_drain(stock)
        assert any("above SMA50 at" in m for m in messages)

    def test_generate_notifications_does_not_add_close_to_sma50_when_beyond_threshold(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="95.00", fifty_day_average="110.00"
        )
        messages = generate_and_drain(stock)
        assert not any("SMA50 at" in m for m in messages)

    def test_generate_notifications_does_not_add_close_to_sma50_when_previous_close_on_same_side(
        self,
    ):
        stock = make_stock(
            current_price="110.00", previous_close_price="108.00", fifty_day_average="100.00"
        )
        messages = generate_and_drain(stock)
        assert not any("SMA50 at" in m for m in messages)


class TestCloseToSMA200Notifications:
    def test_generate_notifications_adds_close_to_sma200_when_approaching_from_below(self):
        stock = open_stock_after_burn(
            current_price="100.00",
            previous_close_price="95.00",
            two_hundred_day_average="102.00",
        )
        messages = generate_and_drain(stock)
        assert any("below SMA200 at" in m for m in messages)

    def test_generate_notifications_adds_close_to_sma200_when_approaching_from_above(self):
        stock = open_stock_after_burn(
            current_price="100.00",
            previous_close_price="105.00",
            two_hundred_day_average="98.00",
        )
        messages = generate_and_drain(stock)
        assert any("above SMA200 at" in m for m in messages)

    def test_generate_notifications_does_not_add_close_to_sma200_when_beyond_threshold(self):
        stock = make_stock(
            current_price="100.00",
            previous_close_price="95.00",
            two_hundred_day_average="110.00",
        )
        messages = generate_and_drain(stock)
        assert not any("SMA200 at" in m for m in messages)

    def test_generate_notifications_does_not_add_close_to_sma200_when_previous_close_on_same_side(
        self,
    ):
        stock = make_stock(
            current_price="110.00",
            previous_close_price="108.00",
            two_hundred_day_average="100.00",
        )
        messages = generate_and_drain(stock)
        assert not any("SMA200 at" in m for m in messages)


class TestPercentageFromPreviousClose:
    def test_generate_notifications_rises_when_positive_percentage(self):
        stock = open_stock_after_burn(current_price="150.00", previous_close_price="100.00")
        messages = generate_and_drain(stock)
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_drops_when_negative_percentage(self):
        stock = open_stock_after_burn(current_price="90.00", previous_close_price="100.00")
        messages = generate_and_drain(stock)
        assert any("dropped to" in m for m in messages)

    def test_generate_notifications_no_percentage_when_prices_are_equal(self):
        stock = make_stock(current_price="100.00", previous_close_price="100.00")
        messages = generate_and_drain(stock)
        assert not any("rose to" in m for m in messages)
        assert not any("dropped to" in m for m in messages)


class TestSMACrossingNotifications:
    def test_generate_notifications_adds_fifty_day_notification(self, sma50_crossing_stock):
        messages = generate_and_drain(sma50_crossing_stock)
        assert len(messages) == 1
        assert any("crossed SMA50" in m for m in messages)

    def test_generate_notifications_adds_two_hundred_day_notification(self, sma200_crossing_stock):
        messages = generate_and_drain(sma200_crossing_stock)
        assert len(messages) == 1
        assert any("crossed SMA200" in m for m in messages)

    def test_generate_notifications_adds_both_notifications(self):
        stock = open_stock_after_burn(
            current_price="150.00",
            previous_close_price="130.00",
            fifty_day_average="145.00",
            two_hundred_day_average="140.00",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert "crossed SMA50" in messages[0]
        assert "crossed SMA200" in messages[0]

    def test_generate_notifications_adds_no_notifications_when_no_crossing(self):
        stock = make_stock(
            current_price="150.00",
            previous_close_price="148.00",
            fifty_day_average="120.00",
            two_hundred_day_average="110.00",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)
        assert not any("crossed SMA50" in m for m in messages)
        assert not any("crossed SMA200" in m for m in messages)


class TestRegularMarketOpenNotifications:
    def test_generate_notifications_adds_regular_market_open_notification(self):
        stock = make_stock(
            current_price="150.00", open_price="149.75", previous_close_price="148.00"
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_generate_notifications_adds_regular_market_open_with_current_price_fallback(self):
        stock = make_stock(current_price="150.00", previous_close_price="148.00")
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_generate_notifications_does_not_add_regular_market_open_when_market_closed(self):
        stock = make_stock(
            current_price="150.00",
            open_price="149.75",
            previous_close_price="148.00",
            market_state=MarketState.CLOSED,
        )
        messages = generate_and_drain(stock)
        assert messages == []

    def test_generate_notifications_returns_empty_when_market_state_is_none(self):
        stock = make_stock(current_price="150.00", market_state=None)
        messages = generate_and_drain(stock)
        assert messages == []


class TestMarketOpenDeferral:
    def test_first_call_returns_only_market_open_notification(self):
        stock = make_stock(
            current_price="106.00", previous_close_price="100.00", fifty_day_average="103.00"
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert "opened at" in messages[0]

    def test_second_call_returns_deferred_notifications(self):
        stock = open_stock_after_burn(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("crossed SMA50" in m for m in messages)

    def test_non_first_open_generates_all_notifications_together(self):
        stock = make_stock(current_price="150.00", previous_close_price="148.00")
        generate_and_drain(stock)
        source = make_stock(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        stock.update(source)

        messages = generate_and_drain(stock)

        assert any("crossed SMA50" in m for m in messages)
        assert any("rose to" in m for m in messages)


class TestMarketStatePost:
    def test_generate_notifications_does_not_add_market_closed_for_non_post_states(self):
        for state in [MarketState.OPEN, MarketState.PRE, MarketState.CLOSED]:
            stock = make_stock(current_price="150.00", market_state=state)
            messages = generate_and_drain(stock)
            assert not any("closed at" in m for m in messages)

    def test_generate_notifications_returns_empty_when_market_state_is_none(self):
        stock = make_stock(current_price="150.00", market_state=None)
        messages = generate_and_drain(stock)
        assert messages == []


class TestRegularMarketClosedNotifications:
    def test_generate_notifications_adds_regular_market_closed_when_post(self):
        stock = make_stock(current_price="150.00", market_state=MarketState.POST)
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("closed at" in m for m in messages)


class TestPercentageChangeNotifications:
    _STOCK_THRESHOLDS = [
        ("104.10", "100.00", "rose to"),
        ("108.10", "100.00", "rose to"),
        ("112.10", "100.00", "rose to"),
        ("116.10", "100.00", "rose to"),
        ("120.10", "100.00", "rose to"),
        ("95.90", "100.00", "dropped to"),
        ("91.90", "100.00", "dropped to"),
        ("87.90", "100.00", "dropped to"),
        ("83.90", "100.00", "dropped to"),
        ("79.90", "100.00", "dropped to"),
    ]

    _DEFAULT_THRESHOLDS = [
        ("100.80", "100.00", "rose to"),
        ("101.60", "100.00", "rose to"),
        ("102.30", "100.00", "rose to"),
        ("103.10", "100.00", "rose to"),
        ("103.80", "100.00", "rose to"),
        ("99.20", "100.00", "dropped to"),
        ("98.40", "100.00", "dropped to"),
        ("97.70", "100.00", "dropped to"),
        ("96.90", "100.00", "dropped to"),
        ("96.20", "100.00", "dropped to"),
    ]

    _CRYPTO_THRESHOLDS = [
        ("102.10", "100.00", "rose to"),
        ("104.10", "100.00", "rose to"),
        ("106.10", "100.00", "rose to"),
        ("108.10", "100.00", "rose to"),
        ("110.10", "100.00", "rose to"),
        ("97.90", "100.00", "dropped to"),
        ("95.90", "100.00", "dropped to"),
        ("93.90", "100.00", "dropped to"),
        ("91.90", "100.00", "dropped to"),
        ("89.90", "100.00", "dropped to"),
    ]

    @pytest.mark.parametrize(
        "current_price, previous_close, expected_text",
        _STOCK_THRESHOLDS,
        ids=[
            "stock_4pct_increase",
            "stock_8pct_increase",
            "stock_12pct_increase",
            "stock_16pct_increase",
            "stock_20pct_increase",
            "stock_4pct_decrease",
            "stock_8pct_decrease",
            "stock_12pct_decrease",
            "stock_16pct_decrease",
            "stock_20pct_decrease",
        ],
    )
    def test_stock_percentage_thresholds(self, current_price, previous_close, expected_text):
        stock = open_stock_after_burn(
            current_price=current_price,
            previous_close_price=previous_close,
            kind=InstrumentType.STOCK,
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any(expected_text in m for m in messages)

    @pytest.mark.parametrize(
        "current_price, previous_close, expected_text",
        _DEFAULT_THRESHOLDS,
        ids=[
            "default_0.75pct_increase",
            "default_1.5pct_increase",
            "default_2.25pct_increase",
            "default_3pct_increase",
            "default_3.75pct_increase",
            "default_0.75pct_decrease",
            "default_1.5pct_decrease",
            "default_2.25pct_decrease",
            "default_3pct_decrease",
            "default_3.75pct_decrease",
        ],
    )
    def test_default_percentage_thresholds(self, current_price, previous_close, expected_text):
        stock = open_stock_after_burn(
            current_price=current_price,
            previous_close_price=previous_close,
            kind=InstrumentType.ETF,
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any(expected_text in m for m in messages)

    @pytest.mark.parametrize(
        "current_price, previous_close, expected_text",
        _CRYPTO_THRESHOLDS,
        ids=[
            "crypto_2pct_increase",
            "crypto_4pct_increase",
            "crypto_6pct_increase",
            "crypto_8pct_increase",
            "crypto_10pct_increase",
            "crypto_2pct_decrease",
            "crypto_4pct_decrease",
            "crypto_6pct_decrease",
            "crypto_8pct_decrease",
            "crypto_10pct_decrease",
        ],
    )
    def test_crypto_percentage_thresholds(self, current_price, previous_close, expected_text):
        stock = make_stock(
            current_price=current_price,
            previous_close_price=previous_close,
            kind=InstrumentType.CRYPTO,
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any(expected_text in m for m in messages)

    def test_index_percentage_thresholds(self):
        stock = open_stock_after_burn(
            current_price="100.80", previous_close_price="100.00", kind=InstrumentType.INDEX
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_none_kind_uses_default_thresholds(self):
        stock = open_stock_after_burn(
            current_price="100.80", previous_close_price="100.00", kind=None
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_stock_no_percentage_below_threshold(self):
        stock = make_stock(
            current_price="103.90",
            previous_close_price="100.00",
            kind=InstrumentType.STOCK,
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_default_no_percentage_below_threshold(self):
        stock = make_stock(
            current_price="100.70",
            previous_close_price="100.00",
            kind=InstrumentType.ETF,
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_stock_percentage_at_exact_threshold(self):
        stock = open_stock_after_burn(
            current_price="104.00",
            previous_close_price="100.00",
            kind=InstrumentType.STOCK,
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_default_percentage_at_exact_threshold(self):
        stock = open_stock_after_burn(
            current_price="100.75",
            previous_close_price="100.00",
            kind=InstrumentType.ETF,
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_no_percentage_when_previous_close_none(self):
        stock = make_stock(current_price="150.00")
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)


class Test52WeekHighNotifications:
    def test_generate_new_52_week_high_notification_does_not_add_when_no_snapshot(self):
        stock = make_stock(current_price="200.00")
        messages = generate_and_drain(stock)
        assert not any("52-week high" in m for m in messages)

    def test_generate_new_52_week_high_notification_does_not_add_when_snapshot_has_no_52_week_high(
        self,
    ):
        stock = make_stock(current_price="180.00")
        source = make_stock(current_price="200.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("52-week high" in m for m in messages)

    def test_generate_new_52_week_high_notification_does_not_add_when_current_price_equals_snapshot_52_week_high(
        self,
    ):
        stock = make_stock(current_price="170.00", fifty_two_week_high="180.00")
        source = make_stock(current_price="180.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("52-week high" in m for m in messages)

    def test_generate_new_52_week_high_notification_does_not_add_when_current_price_below_snapshot_52_week_high(
        self,
    ):
        stock = make_stock(current_price="160.00", fifty_two_week_high="180.00")
        source = make_stock(current_price="170.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("52-week high" in m for m in messages)

    def test_generate_new_52_week_high_notification_does_not_add_when_no_previous_close(
        self,
    ):
        stock = make_stock(current_price="170.00", fifty_two_week_high="180.00")
        generate_and_drain(stock)
        source = make_stock(current_price="200.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("52-week high" in m for m in messages)

    def test_generate_new_52_week_high_notification_adds_when_current_price_exceeds_snapshot_52_week_high(
        self,
    ):
        stock = open_stock_after_burn(
            current_price="170.00",
            previous_close_price="160.00",
            fifty_two_week_high="180.00",
        )
        stock.update(make_stock(current_price="200.00", previous_close_price="160.00"))
        messages = generate_and_drain(stock)
        assert any("52-week high" in m for m in messages)


class Test52WeekLowNotifications:
    def test_generate_new_52_week_low_notification_does_not_add_when_no_snapshot(self):
        stock = make_stock(current_price="100.00")
        messages = generate_and_drain(stock)
        assert not any("52-week low" in m for m in messages)

    def test_generate_new_52_week_low_notification_does_not_add_when_snapshot_has_no_52_week_low(
        self,
    ):
        stock = make_stock(current_price="120.00")
        source = make_stock(current_price="100.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("52-week low" in m for m in messages)

    def test_generate_new_52_week_low_notification_does_not_add_when_current_price_equals_snapshot_52_week_low(
        self,
    ):
        stock = make_stock(current_price="130.00", fifty_two_week_low="120.00")
        source = make_stock(current_price="120.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("52-week low" in m for m in messages)

    def test_generate_new_52_week_low_notification_does_not_add_when_current_price_above_snapshot_52_week_low(
        self,
    ):
        stock = make_stock(current_price="140.00", fifty_two_week_low="120.00")
        source = make_stock(current_price="130.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("52-week low" in m for m in messages)

    def test_generate_new_52_week_low_notification_does_not_add_when_no_previous_close(
        self,
    ):
        stock = make_stock(current_price="130.00", fifty_two_week_low="120.00")
        generate_and_drain(stock)
        source = make_stock(current_price="100.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("52-week low" in m for m in messages)

    def test_generate_new_52_week_low_notification_adds_when_current_price_falls_below_snapshot_52_week_low(
        self,
    ):
        stock = open_stock_after_burn(
            current_price="130.00",
            previous_close_price="125.00",
            fifty_two_week_low="120.00",
        )
        stock.update(make_stock(current_price="100.00", previous_close_price="125.00"))
        messages = generate_and_drain(stock)
        assert any("52-week low" in m for m in messages)


class TestPriceDelayField:
    def test_stock_price_delay_in_minutes_accepts_int_and_none(self):
        stock_real_time = Stock(
            symbol="AAPL", current_price=Decimal("150.00"), price_delay_in_minutes=0
        )
        assert stock_real_time.price_delay_in_minutes == 0

        stock_delayed = Stock(
            symbol="AAPL", current_price=Decimal("150.00"), price_delay_in_minutes=15
        )
        assert stock_delayed.price_delay_in_minutes == 15

        stock_none = Stock(symbol="AAPL", current_price=Decimal("150.00"))
        assert stock_none.price_delay_in_minutes is None


class TestUpdate:
    def test_snapshot_defaults_to_none(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

        assert stock.snapshot is None

    def test_update_captures_snapshot_of_previous_state(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            fifty_two_week_high=Decimal("160.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=0,
        )
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("155.00"),
            fifty_two_week_high=Decimal("165.00"),
            market_state=MarketState.OPEN,
        )

        stock.update(source)

        assert stock.snapshot is not None
        assert stock.snapshot.current_price == Decimal("150.00")
        assert stock.snapshot.fifty_two_week_high == Decimal("160.00")
        assert stock.snapshot.market_state == MarketState.OPEN
        assert stock.snapshot.price_delay_in_minutes == 0

    def test_update_copies_fields_from_source(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("155.00"),
            name="Apple Inc.",
            currency="USD",
            previous_close_price=Decimal("149.00"),
            open_price=Decimal("150.00"),
            day_high=Decimal("156.00"),
            day_low=Decimal("148.00"),
            fifty_day_average=Decimal("145.00"),
            two_hundred_day_average=Decimal("140.00"),
            fifty_two_week_high=Decimal("170.00"),
            fifty_two_week_low=Decimal("120.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
        )

        stock.update(source)

        assert stock.current_price == Decimal("155.00")
        assert stock.name == "Apple Inc."
        assert stock.currency == "USD"
        assert stock.previous_close_price == Decimal("149.00")
        assert stock.open_price == Decimal("150.00")
        assert stock.day_high == Decimal("156.00")
        assert stock.day_low == Decimal("148.00")
        assert stock.fifty_day_average == Decimal("145.00")
        assert stock.two_hundred_day_average == Decimal("140.00")
        assert stock.fifty_two_week_high == Decimal("170.00")
        assert stock.fifty_two_week_low == Decimal("120.00")
        assert stock.market_state == MarketState.OPEN
        assert stock.price_delay_in_minutes == 15

    def test_update_preserves_symbol(self):
        stock = make_stock(current_price="150.00")
        source = make_stock(current_price="155.00")
        stock.update(source)
        assert stock.symbol == "AAPL"

    def test_update_preserves_notifications(self):
        stock = make_stock(current_price="150.00", previous_close_price="148.00")
        result1 = generate_and_drain(stock)
        assert len(result1) > 0

        source = make_stock(current_price="155.00")
        stock.update(source)

        result2 = generate_and_drain(stock)
        assert result2 == []  # dedup works — notifications survived the update

    def test_stock_snapshot_is_frozen(self):
        snapshot = StockSnapshot(
            current_price=Decimal("150.00"),
            previous_close_price=None,
            open_price=None,
            day_high=None,
            day_low=None,
            fifty_day_average=None,
            two_hundred_day_average=None,
            fifty_two_week_high=None,
            fifty_two_week_low=None,
            market_state=None,
            price_delay_in_minutes=None,
        )

        try:
            snapshot.current_price = Decimal("200.00")
            assert False, "Should not be able to modify frozen dataclass"
        except AttributeError:
            pass


class TestMarketStateTransition:
    def test_is_market_state_transition_returns_false_when_no_snapshot(self):
        stock = make_stock(current_price="150.00")
        assert stock.is_market_state_transition() is False

    def test_is_market_state_transition_returns_true_when_pre_to_open(self):
        stock = make_stock(current_price="150.00", market_state=MarketState.PRE)
        source = make_stock(current_price="155.00", market_state=MarketState.OPEN)
        stock.update(source)
        assert stock.is_market_state_transition() is True

    def test_is_market_state_transition_returns_true_when_open_to_post(self):
        stock = make_stock(current_price="150.00", market_state=MarketState.OPEN)
        source = make_stock(current_price="155.00", market_state=MarketState.POST)
        stock.update(source)
        assert stock.is_market_state_transition() is True

    def test_is_market_state_transition_returns_false_when_same_state(self):
        stock = make_stock(current_price="150.00", market_state=MarketState.OPEN)
        source = make_stock(current_price="155.00", market_state=MarketState.OPEN)
        stock.update(source)
        assert stock.is_market_state_transition() is False

    def test_is_market_state_transition_returns_false_when_transition_to_non_open_post(self):
        stock = make_stock(current_price="150.00", market_state=MarketState.OPEN)
        source = make_stock(current_price="155.00", market_state=MarketState.PRE)
        stock.update(source)
        assert stock.is_market_state_transition() is False


class TestDeduplication:
    def test_generate_notifications_deduplicates_by_type(self):
        stock = make_stock(current_price="150.00", previous_close_price="149.50")
        result1 = generate_and_drain(stock)
        assert len(result1) > 0

        result2 = generate_and_drain(stock)

        assert result2 == []

    def test_generate_notifications_returns_new_notifications_only(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("101.00"),
            previous_close_price=Decimal("99.00"),
            fifty_day_average=Decimal("100.00"),
            two_hundred_day_average=Decimal("80.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        result1 = stock.drain_notifications()
        assert len(result1) > 0
        stock.generate_notifications()
        result2 = stock.drain_notifications()
        assert len(result2) > 0

        stock.generate_notifications()
        result3 = stock.drain_notifications()

        assert result3 == []


class TestNotificationSuppressionRules:
    # --- Rule: close-to-SMA suppressed by same SMA crossing ---

    def test_close_to_sma50_suppressed_by_sma50_crossing(self):
        stock = open_stock_after_burn(
            current_price="101.00", previous_close_price="99.00", fifty_day_average="100.00"
        )
        first_messages = generate_and_drain(stock)
        assert any("crossed SMA50" in m for m in first_messages)

        stock.update(
            make_stock(
                current_price="102.00", previous_close_price="101.00", fifty_day_average="100.00"
            )
        )
        messages = generate_and_drain(stock)
        assert not any("SMA50 at" in m for m in messages)

    def test_close_to_sma200_suppressed_by_sma200_crossing(self):
        stock = open_stock_after_burn(
            current_price="101.00", previous_close_price="99.00", two_hundred_day_average="100.00"
        )
        first_messages = generate_and_drain(stock)
        assert any("crossed SMA200" in m for m in first_messages)

        stock.update(
            make_stock(
                current_price="102.00",
                previous_close_price="101.00",
                two_hundred_day_average="100.00",
            )
        )
        messages = generate_and_drain(stock)
        assert not any("SMA200 at" in m for m in messages)

    def test_close_to_sma50_not_suppressed_when_no_crossing(self):
        stock = open_stock_after_burn(
            current_price="98.00", previous_close_price="95.00", fifty_day_average="100.00"
        )
        messages = generate_and_drain(stock)
        assert any("below SMA50 at" in m for m in messages)

    def test_close_to_sma200_not_suppressed_when_no_crossing(self):
        stock = open_stock_after_burn(
            current_price="98.00", previous_close_price="95.00", two_hundred_day_average="100.00"
        )
        messages = generate_and_drain(stock)
        assert any("below SMA200 at" in m for m in messages)

    # --- Rule: percentage change suppressed by SMA events ---

    def test_percentage_suppressed_by_sma50_crossing(self, sma50_crossing_stock):
        messages = generate_and_drain(sma50_crossing_stock)
        assert any("crossed SMA50" in m for m in messages)
        assert not any("rose to 150" in m and "crossed" not in m for m in messages)

    def test_percentage_suppressed_by_sma200_crossing(self, sma200_crossing_stock):
        messages = generate_and_drain(sma200_crossing_stock)
        assert any("crossed SMA200" in m for m in messages)
        assert not any("rose to 150" in m and "crossed" not in m for m in messages)

    def test_percentage_suppressed_by_close_to_sma50(self, close_to_sma50_from_below_stock):
        messages = generate_and_drain(close_to_sma50_from_below_stock)
        assert any("SMA50 at" in m for m in messages)
        assert not any("rose to 100" in m and "SMA" not in m for m in messages)

    def test_percentage_suppressed_by_close_to_sma200(self, close_to_sma200_from_below_stock):
        messages = generate_and_drain(close_to_sma200_from_below_stock)
        assert any("SMA200 at" in m for m in messages)
        assert not any("rose to 100" in m and "SMA" not in m for m in messages)

    def test_percentage_not_suppressed_without_sma(self):
        stock = open_stock_after_burn(current_price="106.00", previous_close_price="100.00")
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_percentage_dedup_preserved_after_sma_suppression(self, sma50_crossing_stock):
        generate_and_drain(sma50_crossing_stock)
        messages = generate_and_drain(sma50_crossing_stock)
        assert not any("rose to" in m and "crossed" not in m for m in messages)

    # --- Rule: percentage change suppressed by 52-week events ---

    def test_percentage_suppressed_by_new_52_week_high(self):
        stock = open_stock_after_burn(
            current_price="170.00", previous_close_price="160.00", fifty_two_week_high="180.00"
        )
        stock.update(make_stock(current_price="200.00", previous_close_price="160.00"))
        messages = generate_and_drain(stock)
        assert any("52-week high" in m for m in messages)
        assert not any("rose to" in m and "52-week" not in m for m in messages)

    def test_percentage_suppressed_by_new_52_week_low(self):
        stock = open_stock_after_burn(
            current_price="130.00", previous_close_price="125.00", fifty_two_week_low="120.00"
        )
        stock.update(make_stock(current_price="100.00", previous_close_price="125.00"))
        messages = generate_and_drain(stock)
        assert any("52-week low" in m for m in messages)
        assert not any("dropped to" in m and "52-week" not in m for m in messages)

    def test_percentage_dedup_preserved_after_52_week_suppression(self):
        stock = open_stock_after_burn(
            current_price="170.00", previous_close_price="160.00", fifty_two_week_high="180.00"
        )
        stock.update(make_stock(current_price="200.00", previous_close_price="160.00"))
        generate_and_drain(stock)
        messages = generate_and_drain(stock)
        assert not any("rose to" in m and "52-week" not in m for m in messages)

    # --- Rule: session gains/losses erased is never suppressed ---

    def test_gains_erased_not_suppressed_by_sma(self):
        stock = make_stock(
            current_price="121.00", previous_close_price="100.00", fifty_day_average="110.00"
        )
        generate_and_drain(stock)
        generate_and_drain(stock)
        source = make_stock(
            current_price="99.00", previous_close_price="100.00", fifty_day_average="100.50"
        )
        stock.update(source)
        messages = generate_and_drain(stock)
        assert any("erased the session gains" in m for m in messages)


class TestSessionGainsLossesErased:
    def _create_stock_with_percentage_history(self, initial_price, previous_close, final_price):
        """Creates a stock that has gone through: market open → percentage threshold → price change."""
        stock = make_stock(
            current_price=str(initial_price),
            previous_close_price=str(previous_close),
        )
        # Cycle 1: market open
        generate_and_drain(stock)
        # Cycle 2: percentage threshold fires
        generate_and_drain(stock)
        # Update to final price
        source = make_stock(
            current_price=str(final_price),
            previous_close_price=str(previous_close),
        )
        stock.update(source)
        return stock

    def test_gains_erased_fires_when_positive_threshold_recorded_and_price_below_zero(self):
        # +21% triggers threshold, then drops to -1%
        stock = self._create_stock_with_percentage_history(
            Decimal("121.00"), Decimal("100.00"), Decimal("99.00")
        )
        messages = generate_and_drain(stock)
        assert any("erased the session gains" in m for m in messages)

    def test_losses_erased_fires_when_negative_threshold_recorded_and_price_above_zero(self):
        # -10% triggers threshold, then rises to +1%
        stock = self._create_stock_with_percentage_history(
            Decimal("90.00"), Decimal("100.00"), Decimal("101.00")
        )
        messages = generate_and_drain(stock)
        assert any("erased the session losses" in m for m in messages)

    def test_gains_erased_does_not_fire_without_prior_percentage_threshold(self):
        stock = make_stock(current_price="103.00", previous_close_price="100.00")
        generate_and_drain(stock)
        # Price drops below 0% but no percentage threshold was ever recorded
        source = make_stock(current_price="99.00", previous_close_price="100.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("erased the session" in m for m in messages)

    def test_losses_erased_does_not_fire_without_prior_percentage_threshold(self):
        stock = make_stock(current_price="97.00", previous_close_price="100.00")
        generate_and_drain(stock)
        # Price rises above 0% but no percentage threshold was ever recorded
        source = make_stock(current_price="101.00", previous_close_price="100.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("erased the session" in m for m in messages)

    def test_gains_erased_does_not_fire_when_still_positive(self):
        # +21% triggers threshold, drops to +2% (still positive, no crossing)
        stock = self._create_stock_with_percentage_history(
            Decimal("121.00"), Decimal("100.00"), Decimal("102.00")
        )
        messages = generate_and_drain(stock)
        assert not any("erased the session gains" in m for m in messages)

    def test_losses_erased_does_not_fire_when_still_negative(self):
        # -10% triggers threshold, rises to -2% (still negative, no crossing)
        stock = self._create_stock_with_percentage_history(
            Decimal("90.00"), Decimal("100.00"), Decimal("98.00")
        )
        messages = generate_and_drain(stock)
        assert not any("erased the session losses" in m for m in messages)

    def test_gains_erased_dedup_does_not_fire_twice(self):
        stock = self._create_stock_with_percentage_history(
            Decimal("121.00"), Decimal("100.00"), Decimal("99.00")
        )
        generate_and_drain(stock)

        # Next cycle: should not fire again
        messages = generate_and_drain(stock)

        assert not any("erased the session gains" in m for m in messages)

    def test_losses_erased_dedup_does_not_fire_twice(self):
        stock = self._create_stock_with_percentage_history(
            Decimal("90.00"), Decimal("100.00"), Decimal("101.00")
        )
        generate_and_drain(stock)

        messages = generate_and_drain(stock)

        assert not any("erased the session losses" in m for m in messages)

    def test_gains_erased_resets_positive_percentage_notifications(self):
        # Cycle 1: market open
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        # Cycle 2: +10% threshold fires
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("110.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications()
        stock.drain_notifications()
        # Cycle 3: drops to -1% → gains erased fires
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("99.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications()
        messages = stock.drain_notifications()
        assert any("erased the session gains" in m for m in messages)
        # Cycle 4: recovers to +5% → should fire again
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("105.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("+5.00%" in m for m in messages)

    def test_losses_erased_resets_negative_percentage_notifications(self):
        # Cycle 1: market open
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        # Cycle 2: -10% threshold fires
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("90.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications()
        stock.drain_notifications()
        # Cycle 3: rises to +1% → losses erased fires
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("101.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications()
        messages = stock.drain_notifications()
        assert any("erased the session losses" in m for m in messages)
        # Cycle 4: drops to -5% → should fire again
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("95.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("-5.00%" in m for m in messages)


class TestTargetPriceNotifications:
    def test_generate_notifications_appends_target_price_reached_when_target_is_reached(self):
        stock = open_stock_ready_for_target("100.00", "200.00", "200.00")
        messages = generate_and_drain(stock)
        assert any("hit target" in m for m in messages)

    def test_generate_notifications_removes_triggered_targets_from_stock(self):
        stock = open_stock_ready_for_target("100.00", "200.00", "200.00")
        generate_and_drain(stock)
        assert stock.drain_fulfilled_targets() == [Decimal("200.00")]

    def test_generate_notifications_does_not_include_unreached_target(self):
        stock = make_stock(current_price="100.00", previous_close_price="148.00")
        stock.sync_targets([Decimal("200.00")])
        source = make_stock(current_price="150.00", previous_close_price="148.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("hit target" in m for m in messages)
        assert stock.drain_fulfilled_targets() == []

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
        messages = generate_and_drain(stock)
        assert not any("hit target" in m for m in messages)
        assert stock.drain_fulfilled_targets() == []

    def test_generate_notifications_removes_multiple_triggered_targets(self):
        stock = open_stock_after_burn(current_price="100.00", previous_close_price="295.00")
        stock.sync_targets([Decimal("200.00"), Decimal("250.00")])
        source = make_stock(current_price="300.00", previous_close_price="295.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        target_messages = [m for m in messages if "hit target" in m]
        assert len(target_messages) == 2
        assert set(stock.drain_fulfilled_targets()) == {Decimal("200.00"), Decimal("250.00")}

    def test_generate_notifications_target_price_reached_is_never_deduplicated(self):
        stock = open_stock_after_burn(current_price="100.00", previous_close_price="195.00")
        stock.sync_targets([Decimal("200.00")])
        source1 = make_stock(current_price="200.00", previous_close_price="195.00")
        stock.update(source1)
        stock.generate_notifications()
        result1 = stock.drain_notifications()
        assert any("hit target" in m for m in result1)

        stock.sync_targets([Decimal("250.00")])
        source2 = make_stock(current_price="250.00", previous_close_price="195.00")
        stock.update(source2)
        stock.generate_notifications()
        result2 = stock.drain_notifications()
        assert any("hit target" in m for m in result2)


class TestSyncTargets:
    def test_sync_targets_sets_entry_price(self):
        stock = make_stock(current_price="150.00")
        stock.sync_targets([Decimal("200.00")])

        source_below = make_stock(current_price="180.00", previous_close_price="148.00")
        stock.update(source_below)
        generate_and_drain(stock)
        assert not any("hit target" in m for m in [])
        assert stock.drain_fulfilled_targets() == []

        source_hit = make_stock(current_price="200.00", previous_close_price="195.00")
        stock.update(source_hit)
        messages = generate_and_drain(stock)
        assert any("hit target" in m for m in messages)

    def test_sync_targets_removes_missing_targets(self):
        stock = make_stock(current_price="150.00")
        generate_and_drain(stock)
        stock.sync_targets([Decimal("200.00"), Decimal("250.00")])
        stock.sync_targets([Decimal("200.00")])

        source = make_stock(current_price="260.00", previous_close_price="148.00")
        stock.update(source)
        generate_and_drain(stock)

        assert stock.drain_fulfilled_targets() == [Decimal("200.00")]

    def test_sync_targets_clears_all_on_empty_list(self):
        stock = make_stock(current_price="150.00")
        stock.sync_targets([Decimal("200.00")])
        stock.sync_targets([])

        source = make_stock(current_price="200.00", previous_close_price="148.00")
        stock.update(source)
        generate_and_drain(stock)

        assert stock.drain_fulfilled_targets() == []

    def test_sync_targets_adds_new_and_preserves_existing(self):
        stock = make_stock(current_price="150.00")
        generate_and_drain(stock)
        stock.sync_targets([Decimal("200.00")])
        stock.sync_targets([Decimal("200.00"), Decimal("250.00")])

        source = make_stock(current_price="260.00", previous_close_price="148.00")
        stock.update(source)
        generate_and_drain(stock)

        assert set(stock.drain_fulfilled_targets()) == {Decimal("200.00"), Decimal("250.00")}


class TestDrainFulfilledTargets:
    def test_drain_fulfilled_targets_returns_fulfilled_targets(self):
        stock = open_stock_after_burn(current_price="150.00", previous_close_price="145.00")
        stock.sync_targets([Decimal("150.00")])
        generate_and_drain(stock)

        fulfilled = stock.drain_fulfilled_targets()

        assert len(fulfilled) == 1
        assert fulfilled[0] == Decimal("150.00")

    def test_drain_fulfilled_targets_clears_list_after_drain(self):
        stock = make_stock(current_price="150.00", previous_close_price="145.00")
        stock.sync_targets([Decimal("150.00")])
        generate_and_drain(stock)
        stock.drain_fulfilled_targets()

        second_drain = stock.drain_fulfilled_targets()

        assert second_drain == []

    def test_drain_fulfilled_targets_returns_empty_when_no_targets_fulfilled(self):
        stock = make_stock(current_price="150.00", previous_close_price="145.00")
        stock.sync_targets([Decimal("200.00")])
        generate_and_drain(stock)

        fulfilled = stock.drain_fulfilled_targets()

        assert fulfilled == []


class TestCryptoNotifications:
    def test_crypto_open_market_state_generates_no_notifications(self):
        stock = Stock(
            symbol="BTC-USD",
            current_price=Decimal("50000.00"),
            market_state=MarketState.OPEN,
            kind=InstrumentType.CRYPTO,
        )

        messages = generate_and_drain(stock)

        assert messages == []

    def test_crypto_post_market_state_generates_no_notifications(self):
        stock = Stock(
            symbol="BTC-USD",
            current_price=Decimal("50000.00"),
            market_state=MarketState.POST,
            kind=InstrumentType.CRYPTO,
        )

        messages = generate_and_drain(stock)

        assert messages == []

    def test_non_crypto_open_market_state_generates_market_open_notification(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            kind=InstrumentType.STOCK,
        )

        messages = generate_and_drain(stock)

        assert any("open" in m.lower() for m in messages)


class TestConsolidatedNotifications:
    def test_single_milestone_produces_header_with_bullet(self):
        stock = open_stock_after_burn(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        lines = messages[0].split("\n")
        assert len(lines) == 2
        assert "rose to 150.00" in lines[0]
        assert lines[1] == "⚠️ crossed SMA50 at 145.00"

    def test_multiple_milestones_produce_single_consolidated_message(self):
        stock = open_stock_after_burn(
            current_price="150.00",
            previous_close_price="130.00",
            fifty_day_average="145.00",
            two_hundred_day_average="140.00",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        lines = messages[0].split("\n")
        assert len(lines) == 3
        assert "rose to 150.00" in lines[0]
        assert "⚠️ crossed SMA50" in lines[1]
        assert "⚠️ crossed SMA200" in lines[2]

    def test_percentage_suppressed_when_milestones_exist(self):
        stock = open_stock_after_burn(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        lines = messages[0].split("\n")
        # Only header + milestone bullet, no separate percentage line
        assert len(lines) == 2

    def test_header_only_emitted_when_no_milestones(self):
        stock = open_stock_after_burn(current_price="106.00", previous_close_price="100.00")
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert "\n" not in messages[0]
        assert "rose to" in messages[0]

    def test_standalone_messages_emitted_separately(self):
        stock = make_stock(
            current_price="150.00", open_price="149.75", previous_close_price="148.00"
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert "opened at" in messages[0]

    def test_targets_emitted_separately_from_consolidated_milestones(self):
        stock = open_stock_after_burn(
            current_price="100.00",
            previous_close_price="95.00",
            fifty_day_average="102.00",
        )
        stock.sync_targets([Decimal("100.00")])
        messages = generate_and_drain(stock)
        consolidated = [m for m in messages if "\n" in m or "SMA50" in m]
        targets = [m for m in messages if "hit target" in m]
        assert len(consolidated) == 1
        assert len(targets) == 1

    def test_percentage_dedup_preserved_after_consolidation_suppression(self):
        stock = open_stock_after_burn(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        generate_and_drain(stock)
        # Second cycle: percentage should not reappear (moved to historical during drain)
        messages = generate_and_drain(stock)
        assert not any("rose to" in m for m in messages)

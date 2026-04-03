from datetime import datetime
from decimal import Decimal

import pytest

from pryces.domain.notification_formatter import ConsolidatingNotificationFormatter
from pryces.domain.stocks import (
    Currency,
    InstrumentType,
    MarketState,
    Stock,
)
from tests.fixtures.factories import (
    _DEFAULT_NOW,
    generate_and_drain,
    make_stock,
    make_stock_with_percentage_history,
    open_stock_after_burn,
)

_formatter = ConsolidatingNotificationFormatter()


class TestHasCrossedSMA:
    def test_has_crossed_sma_returns_false_when_fields_are_missing(self):
        stock = make_stock(current_price="150.00")
        messages = generate_and_drain(stock)
        assert not any("Crossed SMA50" in m for m in messages)

        stock_with_previous = make_stock(current_price="150.00", previous_close_price="140.00")
        messages = generate_and_drain(stock_with_previous)
        assert not any("Crossed SMA50" in m for m in messages)

        stock_with_average = make_stock(current_price="150.00", fifty_day_average="145.00")
        messages = generate_and_drain(stock_with_average)
        assert not any("Crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_above(self):
        stock = make_stock(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert any("Crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_below(self):
        stock = make_stock(
            current_price="140.00",
            previous_close_price="150.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert any("Crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_returns_false_when_no_crossing(self):
        stock_both_above = make_stock(
            current_price="150.00", previous_close_price="148.00", fifty_day_average="145.00"
        )
        messages = generate_and_drain(stock_both_above)
        assert not any("Crossed SMA50" in m for m in messages)

        stock_both_below = make_stock(
            current_price="140.00", previous_close_price="142.00", fifty_day_average="145.00"
        )
        messages = generate_and_drain(stock_both_below)
        assert not any("Crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_above_when_current_equals_average(self):
        stock = make_stock(
            current_price="145.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert any("Crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_below_when_current_equals_average(self):
        stock = make_stock(
            current_price="145.00",
            previous_close_price="150.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert any("Crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_returns_false_when_previous_equals_average(self):
        stock_current_above = make_stock(
            current_price="150.00", previous_close_price="145.00", fifty_day_average="145.00"
        )
        messages = generate_and_drain(stock_current_above)
        assert not any("Crossed SMA50" in m for m in messages)

        stock_current_below = make_stock(
            current_price="140.00", previous_close_price="145.00", fifty_day_average="145.00"
        )
        messages = generate_and_drain(stock_current_below)
        assert not any("Crossed SMA50" in m for m in messages)


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

    def test_is_close_to_sma_returns_true_when_approaching_from_below_within_threshold(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="95.00", fifty_day_average="102.00"
        )
        messages = generate_and_drain(stock)
        assert any("Below SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_true_when_approaching_from_above_within_threshold(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="105.00", fifty_day_average="98.00"
        )
        messages = generate_and_drain(stock)
        assert any("Above SMA50 at" in m for m in messages)

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

    def test_is_close_to_sma_returns_true_at_exact_threshold_from_below(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="95.00", fifty_day_average="102.00"
        )
        messages = generate_and_drain(stock)
        assert any("Below SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_true_at_exact_threshold_from_above(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="105.00", fifty_day_average="98.00"
        )
        messages = generate_and_drain(stock)
        assert any("Above SMA50 at" in m for m in messages)

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
        stock = make_stock(
            current_price="100.00", previous_close_price="95.00", fifty_day_average="102.00"
        )
        messages = generate_and_drain(stock)
        assert any("Below SMA50 at" in m for m in messages)

    def test_generate_notifications_adds_close_to_sma50_when_approaching_from_above(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="105.00", fifty_day_average="98.00"
        )
        messages = generate_and_drain(stock)
        assert any("Above SMA50 at" in m for m in messages)

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
        stock = make_stock(
            current_price="100.00",
            previous_close_price="95.00",
            two_hundred_day_average="102.00",
        )
        messages = generate_and_drain(stock)
        assert any("Below SMA200 at" in m for m in messages)

    def test_generate_notifications_adds_close_to_sma200_when_approaching_from_above(self):
        stock = make_stock(
            current_price="100.00",
            previous_close_price="105.00",
            two_hundred_day_average="98.00",
        )
        messages = generate_and_drain(stock)
        assert any("Above SMA200 at" in m for m in messages)

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
        stock = make_stock(current_price="100.00", previous_close_price="100.00")
        generate_and_drain(stock)
        stock.update(make_stock(current_price="150.00", previous_close_price="100.00"))
        messages = generate_and_drain(stock)
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_drops_when_negative_percentage(self):
        stock = make_stock(current_price="100.00", previous_close_price="100.00")
        generate_and_drain(stock)
        stock.update(make_stock(current_price="90.00", previous_close_price="100.00"))
        messages = generate_and_drain(stock)
        assert any("dropped to" in m for m in messages)

    def test_generate_notifications_no_percentage_when_prices_are_equal(self):
        stock = make_stock(current_price="100.00", previous_close_price="100.00")
        messages = generate_and_drain(stock)
        assert not any("rose to" in m for m in messages)
        assert not any("dropped to" in m for m in messages)


class TestSMACrossingNotifications:
    def test_generate_notifications_adds_fifty_day_notification(self):
        stock = make_stock(
            current_price="150.00", previous_close_price="140.00", fifty_day_average="145.00"
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("Crossed SMA50" in m for m in messages)

    def test_generate_notifications_adds_two_hundred_day_notification(self):
        stock = make_stock(
            current_price="150.00", previous_close_price="130.00", two_hundred_day_average="140.00"
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("Crossed SMA200" in m for m in messages)

    def test_generate_notifications_adds_both_notifications(self):
        stock = make_stock(
            current_price="150.00",
            previous_close_price="130.00",
            fifty_day_average="145.00",
            two_hundred_day_average="140.00",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert "Crossed SMA50" in messages[0]
        assert "Crossed SMA200" in messages[0]

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
        assert not any("Crossed SMA50" in m for m in messages)
        assert not any("Crossed SMA200" in m for m in messages)


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


class TestMarketOpenWithOtherNotifications:
    def test_market_open_generates_all_notifications_on_first_call(self):
        stock = make_stock(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert "opened at" in messages[0]
        assert "Crossed SMA50" in messages[0]

    def test_market_open_as_header_with_milestones(self):
        stock = make_stock(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        lines = messages[0].split("\n")
        assert "opened at" in lines[0]
        assert any("Crossed SMA50" in l for l in lines)

    def test_market_open_alone_when_no_milestones(self):
        stock = make_stock(current_price="150.00", previous_close_price="148.00")
        messages = generate_and_drain(stock)
        assert any("opened at" in m for m in messages)

    def test_market_open_absorbs_percentage_into_single_message(self):
        stock = make_stock(current_price="106.00", previous_close_price="100.00")
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert "opened at" in messages[0]


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
        ("107.60", "100.00", "rose to"),
        ("111.10", "100.00", "rose to"),
        ("114.60", "100.00", "rose to"),
        ("118.10", "100.00", "rose to"),
        ("95.90", "100.00", "dropped to"),
        ("92.40", "100.00", "dropped to"),
        ("88.90", "100.00", "dropped to"),
        ("85.40", "100.00", "dropped to"),
        ("81.90", "100.00", "dropped to"),
    ]

    _DEFAULT_THRESHOLDS = [
        ("102.10", "100.00", "rose to"),
        ("103.80", "100.00", "rose to"),
        ("105.60", "100.00", "rose to"),
        ("107.30", "100.00", "rose to"),
        ("109.10", "100.00", "rose to"),
        ("97.90", "100.00", "dropped to"),
        ("96.20", "100.00", "dropped to"),
        ("94.40", "100.00", "dropped to"),
        ("92.70", "100.00", "dropped to"),
        ("90.90", "100.00", "dropped to"),
    ]

    @pytest.mark.parametrize(
        "current_price, previous_close, expected_text",
        _STOCK_THRESHOLDS,
        ids=[
            "stock_4pct_increase",
            "stock_7.5pct_increase",
            "stock_11pct_increase",
            "stock_14.5pct_increase",
            "stock_18pct_increase",
            "stock_4pct_decrease",
            "stock_7.5pct_decrease",
            "stock_11pct_decrease",
            "stock_14.5pct_decrease",
            "stock_18pct_decrease",
        ],
    )
    def test_stock_percentage_thresholds(self, current_price, previous_close, expected_text):
        stock = make_stock(
            current_price=previous_close,
            previous_close_price=previous_close,
            kind=InstrumentType.STOCK,
        )
        generate_and_drain(stock)
        stock.update(
            make_stock(
                current_price=current_price,
                previous_close_price=previous_close,
                kind=InstrumentType.STOCK,
            )
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any(expected_text in m for m in messages)

    @pytest.mark.parametrize(
        "current_price, previous_close, expected_text",
        _DEFAULT_THRESHOLDS,
        ids=[
            "default_2pct_increase",
            "default_3.75pct_increase",
            "default_5.5pct_increase",
            "default_7.25pct_increase",
            "default_9pct_increase",
            "default_2pct_decrease",
            "default_3.75pct_decrease",
            "default_5.5pct_decrease",
            "default_7.25pct_decrease",
            "default_9pct_decrease",
        ],
    )
    def test_default_percentage_thresholds(self, current_price, previous_close, expected_text):
        stock = make_stock(
            current_price=previous_close,
            previous_close_price=previous_close,
            kind=InstrumentType.ETF,
        )
        generate_and_drain(stock)
        stock.update(
            make_stock(
                current_price=current_price,
                previous_close_price=previous_close,
                kind=InstrumentType.ETF,
            )
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any(expected_text in m for m in messages)

    @pytest.mark.parametrize(
        "current_price, previous_close, expected_text",
        _DEFAULT_THRESHOLDS,
        ids=[
            "crypto_2pct_increase",
            "crypto_3.75pct_increase",
            "crypto_5.5pct_increase",
            "crypto_7.25pct_increase",
            "crypto_9pct_increase",
            "crypto_2pct_decrease",
            "crypto_3.75pct_decrease",
            "crypto_5.5pct_decrease",
            "crypto_7.25pct_decrease",
            "crypto_9pct_decrease",
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
        stock = make_stock(
            current_price="100.00", previous_close_price="100.00", kind=InstrumentType.INDEX
        )
        generate_and_drain(stock)
        stock.update(
            make_stock(
                current_price="101.10", previous_close_price="100.00", kind=InstrumentType.INDEX
            )
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_none_kind_uses_default_thresholds(self):
        stock = make_stock(current_price="100.00", previous_close_price="100.00", kind=None)
        generate_and_drain(stock)
        stock.update(make_stock(current_price="102.10", previous_close_price="100.00", kind=None))
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_large_cap_stock_uses_level_2_thresholds(self):
        stock = make_stock(
            current_price="100.00",
            previous_close_price="100.00",
            kind=InstrumentType.STOCK,
            currency=Currency.USD,
            market_cap="15000000000",
        )
        generate_and_drain(stock)
        stock.update(
            make_stock(
                current_price="102.10",
                previous_close_price="100.00",
                kind=InstrumentType.STOCK,
                currency=Currency.USD,
                market_cap="15000000000",
            )
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_large_cap_stock_no_notification_below_level_2_threshold(self):
        stock = make_stock(
            current_price="101.90",
            previous_close_price="100.00",
            kind=InstrumentType.STOCK,
            currency=Currency.USD,
            market_cap="15000000000",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_large_cap_stock_at_exact_level_2_threshold(self):
        stock = make_stock(
            current_price="100.00",
            previous_close_price="100.00",
            kind=InstrumentType.STOCK,
            currency=Currency.USD,
            market_cap="15000000000",
        )
        generate_and_drain(stock)
        stock.update(
            make_stock(
                current_price="102.00",
                previous_close_price="100.00",
                kind=InstrumentType.STOCK,
                currency=Currency.USD,
                market_cap="15000000000",
            )
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_mid_cap_stock_still_uses_level_3_thresholds(self):
        stock = make_stock(
            current_price="102.10",
            previous_close_price="100.00",
            kind=InstrumentType.STOCK,
            currency=Currency.USD,
            market_cap="5000000000",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_small_cap_stock_still_uses_level_3_thresholds(self):
        stock = make_stock(
            current_price="102.10",
            previous_close_price="100.00",
            kind=InstrumentType.STOCK,
            currency=Currency.USD,
            market_cap="1000000000",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_stock_with_unknown_cap_still_uses_level_3_thresholds(self):
        stock = make_stock(
            current_price="102.10",
            previous_close_price="100.00",
            kind=InstrumentType.STOCK,
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

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
            current_price="101.90",
            previous_close_price="100.00",
            kind=InstrumentType.ETF,
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_stock_percentage_at_exact_threshold(self):
        stock = make_stock(
            current_price="100.00",
            previous_close_price="100.00",
            kind=InstrumentType.STOCK,
        )
        generate_and_drain(stock)
        stock.update(
            make_stock(
                current_price="104.00",
                previous_close_price="100.00",
                kind=InstrumentType.STOCK,
            )
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_default_percentage_at_exact_threshold(self):
        stock = make_stock(
            current_price="100.00",
            previous_close_price="100.00",
            kind=InstrumentType.ETF,
        )
        generate_and_drain(stock)
        stock.update(
            make_stock(
                current_price="102.00",
                previous_close_price="100.00",
                kind=InstrumentType.ETF,
            )
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


class TestSessionGainsLossesErased:
    def test_gains_erased_fires_when_positive_threshold_recorded_and_price_below_zero(self):
        # +21% triggers threshold, then drops to -1%
        stock = make_stock_with_percentage_history(
            Decimal("121.00"), Decimal("100.00"), Decimal("99.00")
        )
        messages = generate_and_drain(stock)
        assert any("Erased session gains" in m for m in messages)

    def test_losses_erased_fires_when_negative_threshold_recorded_and_price_above_zero(self):
        # -10% triggers threshold, then rises to +1%
        stock = make_stock_with_percentage_history(
            Decimal("90.00"), Decimal("100.00"), Decimal("101.00")
        )
        messages = generate_and_drain(stock)
        assert any("Erased session losses" in m for m in messages)

    def test_gains_erased_does_not_fire_without_prior_percentage_threshold(self):
        stock = make_stock(current_price="101.90", previous_close_price="100.00")
        generate_and_drain(stock)
        # Price drops below 0% but no percentage threshold was ever recorded
        source = make_stock(current_price="99.00", previous_close_price="100.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("Erased session" in m for m in messages)

    def test_losses_erased_does_not_fire_without_prior_percentage_threshold(self):
        stock = make_stock(current_price="98.10", previous_close_price="100.00")
        generate_and_drain(stock)
        # Price rises above 0% but no percentage threshold was ever recorded
        source = make_stock(current_price="101.00", previous_close_price="100.00")
        stock.update(source)
        messages = generate_and_drain(stock)
        assert not any("Erased session" in m for m in messages)

    def test_gains_erased_does_not_fire_when_still_positive(self):
        # +21% triggers threshold, drops to +2% (still positive, no crossing)
        stock = make_stock_with_percentage_history(
            Decimal("121.00"), Decimal("100.00"), Decimal("102.00")
        )
        messages = generate_and_drain(stock)
        assert not any("Erased session gains" in m for m in messages)

    def test_losses_erased_does_not_fire_when_still_negative(self):
        # -10% triggers threshold, rises to -2% (still negative, no crossing)
        stock = make_stock_with_percentage_history(
            Decimal("90.00"), Decimal("100.00"), Decimal("98.00")
        )
        messages = generate_and_drain(stock)
        assert not any("Erased session losses" in m for m in messages)

    def test_gains_erased_dedup_does_not_fire_twice(self):
        stock = make_stock_with_percentage_history(
            Decimal("121.00"), Decimal("100.00"), Decimal("99.00")
        )
        generate_and_drain(stock)

        # Next cycle: should not fire again
        messages = generate_and_drain(stock)

        assert not any("Erased session gains" in m for m in messages)

    def test_losses_erased_dedup_does_not_fire_twice(self):
        stock = make_stock_with_percentage_history(
            Decimal("90.00"), Decimal("100.00"), Decimal("101.00")
        )
        generate_and_drain(stock)

        messages = generate_and_drain(stock)

        assert not any("Erased session losses" in m for m in messages)

    def test_gains_erased_resets_positive_percentage_notifications(self):
        # Cycle 1: market open
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications(_DEFAULT_NOW, _formatter)
        # Cycle 2: +10% threshold fires
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("110.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications(_DEFAULT_NOW, _formatter)
        # Cycle 3: drops to -1% → gains erased fires
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("99.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        messages = stock.generate_notifications(_DEFAULT_NOW, _formatter).messages
        assert any("Erased session gains" in m for m in messages)
        # Cycle 4: recovers to +5% → should fire again
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("105.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        messages = stock.generate_notifications(_DEFAULT_NOW, _formatter).messages

        assert any("+5.00%" in m for m in messages)

    def test_losses_erased_resets_negative_percentage_notifications(self):
        # Cycle 1: market open
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications(_DEFAULT_NOW, _formatter)
        # Cycle 2: -10% threshold fires
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("90.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications(_DEFAULT_NOW, _formatter)
        # Cycle 3: rises to +1% → losses erased fires
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("101.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        messages = stock.generate_notifications(_DEFAULT_NOW, _formatter).messages
        assert any("Erased session losses" in m for m in messages)
        # Cycle 4: drops to -5% → should fire again
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("95.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        messages = stock.generate_notifications(_DEFAULT_NOW, _formatter).messages

        assert any("-5.00%" in m for m in messages)


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
        stock = make_stock(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        lines = messages[0].split("\n")
        assert "opened at" in lines[0]
        assert "⚠️ Crossed SMA50 at 145.00" in lines
        assert "rose to" in messages[0]

    def test_multiple_milestones_produce_single_consolidated_message(self):
        stock = make_stock(
            current_price="150.00",
            previous_close_price="130.00",
            fifty_day_average="145.00",
            two_hundred_day_average="140.00",
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        lines = messages[0].split("\n")
        assert "opened at" in lines[0]
        assert any("⚠️ Crossed SMA50" in l for l in lines)
        assert any("⚠️ Crossed SMA200" in l for l in lines)
        assert any("rose to" in l for l in lines)

    def test_header_only_emitted_when_no_milestones(self):
        stock = make_stock(current_price="100.00", previous_close_price="100.00")
        generate_and_drain(stock)
        stock.update(make_stock(current_price="106.00", previous_close_price="100.00"))
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert "\n" not in messages[0]
        assert "rose to" in messages[0]

    def test_market_open_emitted_individually_when_no_milestones(self):
        stock = make_stock(
            current_price="150.00", open_price="149.75", previous_close_price="148.00"
        )
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert "opened at" in messages[0]

    def test_targets_emitted_separately_from_consolidated_milestones(self):
        stock = make_stock(
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
        stock = make_stock(
            current_price="150.00",
            previous_close_price="140.00",
            fifty_day_average="145.00",
        )
        generate_and_drain(stock)
        # Second cycle: percentage should not reappear (moved to historical during drain)
        messages = generate_and_drain(stock)
        assert not any("rose to" in m for m in messages)


class TestDelayWindow:

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

        messages = generate_and_drain(stock)

        assert len(messages) > 0

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

        messages = generate_and_drain(stock)

        assert len(messages) > 0

    def test_suppresses_on_transition_cycle_when_delay_positive(self):
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
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )
        stock.update(source)
        now = datetime(2024, 1, 1, 9, 0, 0)

        messages = generate_and_drain(stock, now=now)

        assert messages == []

    def test_suppresses_during_delay_window(self):
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
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )
        stock.update(source_transition)
        generate_and_drain(stock, now=datetime(2024, 1, 1, 9, 0, 0))

        source_same = Stock(
            symbol="AAPL",
            current_price=Decimal("151.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )
        stock.update(source_same)

        messages = generate_and_drain(stock, now=datetime(2024, 1, 1, 9, 5, 0))

        assert messages == []

    def test_generates_notifications_after_delay_elapsed(self):
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
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )
        stock.update(source_transition)
        generate_and_drain(stock, now=datetime(2024, 1, 1, 9, 0, 0))

        source_same = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )
        stock.update(source_same)

        messages = generate_and_drain(stock, now=datetime(2024, 1, 1, 9, 16, 0))

        assert len(messages) > 0

    def test_no_suppression_when_no_snapshot(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )

        messages = generate_and_drain(stock)

        assert len(messages) > 0

    def test_non_open_post_transitions_not_treated_as_delay_triggers(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
            previous_close_price=Decimal("148.00"),
            open_price=Decimal("149.00"),
        )
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.PRE,
            price_delay_in_minutes=15,
        )
        stock.update(source)

        messages = generate_and_drain(stock)

        assert messages == []

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
            previous_close_price=Decimal("195.00"),
            open_price=Decimal("198.00"),
        )
        stock.update(source)
        now = datetime(2024, 1, 1, 9, 0, 0)

        result = stock.generate_notifications(now, _formatter)

        assert result.messages == []
        assert result.fulfilled_targets == []

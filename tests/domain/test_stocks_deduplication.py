from decimal import Decimal

from pryces.domain.notification_formatter import ConsolidatingNotificationFormatter
from pryces.domain.stocks import (
    InstrumentType,
    MarketState,
    Stock,
)
from tests.fixtures.factories import (
    _DEFAULT_NOW,
    generate_and_drain,
    make_stock,
    open_stock_after_burn,
)

_formatter = ConsolidatingNotificationFormatter()


def has_standalone_percentage_increase(messages: list[str], price: str) -> bool:
    """Returns True if any message contains a standalone 'rose to {price}' (not part of an SMA crossing)."""
    return any(f"rose to {price}" in m and "Crossed" not in m for m in messages)


def has_standalone_percentage_increase_without_sma(messages: list[str], price: str) -> bool:
    """Returns True if any message contains a standalone 'rose to {price}' not grouped with an SMA event."""
    return any(f"rose to {price}" in m and "SMA" not in m for m in messages)


def has_any_standalone_percentage_increase_without_sma(messages: list[str]) -> bool:
    """Returns True if any message contains a 'rose to' percentage change not grouped with an SMA crossing."""
    return any("rose to" in m and "Crossed" not in m for m in messages)


def has_any_standalone_percentage_increase_without_52_week(messages: list[str]) -> bool:
    """Returns True if any message contains a 'rose to' percentage change not grouped with a 52-week event."""
    return any("rose to" in m and "52-week" not in m for m in messages)


def has_any_standalone_percentage_decrease_without_52_week(messages: list[str]) -> bool:
    """Returns True if any message contains a 'dropped to' percentage change not grouped with a 52-week event."""
    return any("dropped to" in m and "52-week" not in m for m in messages)


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
        result1 = stock.generate_notifications(_DEFAULT_NOW, _formatter).messages
        assert len(result1) > 0

        result2 = stock.generate_notifications(_DEFAULT_NOW, _formatter).messages

        assert result2 == []


class TestNotificationSuppressionRules:
    # --- Rule: close-to-SMA suppressed by same SMA crossing ---

    def test_close_to_sma50_suppressed_by_sma50_crossing(self):
        stock = make_stock(
            current_price="101.00", previous_close_price="99.00", fifty_day_average="100.00"
        )
        first_messages = generate_and_drain(stock)
        assert any("Crossed SMA50" in m for m in first_messages)

        stock.update(
            make_stock(
                current_price="102.00", previous_close_price="101.00", fifty_day_average="100.00"
            )
        )
        messages = generate_and_drain(stock)
        assert not any("SMA50 at" in m for m in messages)

    def test_close_to_sma200_suppressed_by_sma200_crossing(self):
        stock = make_stock(
            current_price="101.00", previous_close_price="99.00", two_hundred_day_average="100.00"
        )
        first_messages = generate_and_drain(stock)
        assert any("Crossed SMA200" in m for m in first_messages)

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
        stock = make_stock(
            current_price="98.00", previous_close_price="95.00", fifty_day_average="100.00"
        )
        messages = generate_and_drain(stock)
        assert any("Below SMA50 at" in m for m in messages)

    def test_close_to_sma200_not_suppressed_when_no_crossing(self):
        stock = make_stock(
            current_price="98.00", previous_close_price="95.00", two_hundred_day_average="100.00"
        )
        messages = generate_and_drain(stock)
        assert any("Below SMA200 at" in m for m in messages)

    # --- Rule: percentage change suppressed by SMA events ---

    def test_percentage_suppressed_by_sma50_crossing(self):
        stock = make_stock(
            current_price="150.00", previous_close_price="140.00", fifty_day_average="145.00"
        )
        messages = generate_and_drain(stock)
        assert any("Crossed SMA50" in m for m in messages)
        assert not has_standalone_percentage_increase(messages, "150")

    def test_percentage_suppressed_by_sma200_crossing(self):
        stock = make_stock(
            current_price="150.00", previous_close_price="130.00", two_hundred_day_average="140.00"
        )
        messages = generate_and_drain(stock)
        assert any("Crossed SMA200" in m for m in messages)
        assert not has_standalone_percentage_increase(messages, "150")

    def test_percentage_suppressed_by_close_to_sma50(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="95.00", fifty_day_average="102.00"
        )
        messages = generate_and_drain(stock)
        assert any("SMA50 at" in m for m in messages)
        assert not has_standalone_percentage_increase_without_sma(messages, "100")

    def test_percentage_suppressed_by_close_to_sma200(self):
        stock = make_stock(
            current_price="100.00", previous_close_price="95.00", two_hundred_day_average="102.00"
        )
        messages = generate_and_drain(stock)
        assert any("SMA200 at" in m for m in messages)
        assert not has_standalone_percentage_increase_without_sma(messages, "100")

    def test_percentage_not_suppressed_without_sma(self):
        stock = make_stock(current_price="100.00", previous_close_price="100.00")
        generate_and_drain(stock)
        stock.update(make_stock(current_price="106.00", previous_close_price="100.00"))
        messages = generate_and_drain(stock)
        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_percentage_dedup_preserved_after_sma_suppression(self):
        stock = make_stock(
            current_price="150.00", previous_close_price="140.00", fifty_day_average="145.00"
        )
        generate_and_drain(stock)
        messages = generate_and_drain(stock)
        assert not has_any_standalone_percentage_increase_without_sma(messages)

    # --- Rule: percentage change suppressed by 52-week events ---

    def test_percentage_suppressed_by_new_52_week_high(self):
        stock = open_stock_after_burn(
            current_price="170.00", previous_close_price="160.00", fifty_two_week_high="180.00"
        )
        stock.update(make_stock(current_price="200.00", previous_close_price="160.00"))
        messages = generate_and_drain(stock)
        assert any("52-week high" in m for m in messages)
        assert not has_any_standalone_percentage_increase_without_52_week(messages)

    def test_percentage_suppressed_by_new_52_week_low(self):
        stock = open_stock_after_burn(
            current_price="130.00", previous_close_price="125.00", fifty_two_week_low="120.00"
        )
        stock.update(make_stock(current_price="100.00", previous_close_price="125.00"))
        messages = generate_and_drain(stock)
        assert any("52-week low" in m for m in messages)
        assert not has_any_standalone_percentage_decrease_without_52_week(messages)

    def test_percentage_dedup_preserved_after_52_week_suppression(self):
        stock = open_stock_after_burn(
            current_price="170.00", previous_close_price="160.00", fifty_two_week_high="180.00"
        )
        stock.update(make_stock(current_price="200.00", previous_close_price="160.00"))
        generate_and_drain(stock)
        messages = generate_and_drain(stock)
        assert not has_any_standalone_percentage_increase_without_52_week(messages)

    # --- Rule: percentage change suppressed by market open (same threshold, transient) ---

    def test_percentage_suppressed_when_same_level_as_market_open(self):
        stock = make_stock(
            current_price="106.00",
            previous_close_price="100.00",
            open_price="106.00",
        )
        messages = generate_and_drain(stock)
        assert any("opened at" in m for m in messages)
        assert not any("rose to" in m for m in messages)

    def test_percentage_not_suppressed_when_different_level_from_market_open(self):
        stock = make_stock(
            current_price="120.00",
            previous_close_price="100.00",
            open_price="101.00",
        )
        messages = generate_and_drain(stock)
        assert any("opened at" in m for m in messages)
        assert any("rose to" in m for m in messages)

    def test_percentage_not_suppressed_when_no_market_open(self):
        stock = make_stock(
            current_price="106.00",
            previous_close_price="100.00",
            open_price="106.00",
            kind=InstrumentType.CRYPTO,
        )
        messages = generate_and_drain(stock)
        assert any("rose to" in m for m in messages)

    def test_percentage_stays_suppressed_in_next_cycle_after_market_open_suppression(self):
        stock = make_stock(
            current_price="106.00",
            previous_close_price="100.00",
            open_price="106.00",
        )
        messages1 = generate_and_drain(stock)
        assert any("opened at" in m for m in messages1)
        assert not any("rose to" in m for m in messages1)

        stock.update(
            make_stock(current_price="106.00", previous_close_price="100.00", open_price="106.00")
        )
        messages2 = generate_and_drain(stock)
        assert not any("rose to" in m for m in messages2)

    def test_percentage_suppressed_by_market_open_fires_after_session_erased(self):
        stock = make_stock(
            current_price="106.00",
            previous_close_price="100.00",
            open_price="106.00",
        )
        generate_and_drain(stock)

        stock.update(make_stock(current_price="99.00", previous_close_price="100.00"))
        messages_erased = generate_and_drain(stock)
        assert any("Erased session gains" in m for m in messages_erased)

        stock.update(
            make_stock(current_price="106.00", previous_close_price="100.00", open_price="106.00")
        )
        messages_after = generate_and_drain(stock)
        assert any("rose to" in m for m in messages_after)

    def test_percentage_not_suppressed_when_open_price_is_none(self):
        stock = make_stock(
            current_price="106.00",
            previous_close_price="100.00",
        )
        messages = generate_and_drain(stock)
        assert any("opened at" in m for m in messages)
        assert any("rose to" in m for m in messages)

    # --- Rule: session gains/losses erased is never suppressed ---

    def test_gains_erased_not_suppressed_by_sma(self):
        stock = make_stock(
            current_price="121.00", previous_close_price="100.00", fifty_day_average="110.00"
        )
        generate_and_drain(stock)
        source = make_stock(
            current_price="99.00", previous_close_price="100.00", fifty_day_average="100.50"
        )
        stock.update(source)
        messages = generate_and_drain(stock)
        assert any("Erased session gains" in m for m in messages)

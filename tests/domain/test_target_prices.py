from decimal import Decimal

from pryces.domain.notifications import NotificationType
from pryces.domain.target_prices import TargetPrice
from tests.fixtures.factories import create_stock


class TestTargetPriceConstruction:
    def test_sets_symbol(self):
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        assert pt.symbol == "AAPL"

    def test_sets_target_price(self):
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        assert pt.target_price == Decimal("200.00")

    def test_entry_price_is_none_by_default(self):
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        assert pt.entry_price is None


class TestSetEntryPrice:
    def test_sets_entry_price_from_stock_current_price(self):
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        stock = create_stock("AAPL", Decimal("150.00"))
        pt.set_entry_price(stock)
        assert pt.entry_price == Decimal("150.00")

    def test_overwrites_previous_entry_price(self):
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("150.00")))
        pt.set_entry_price(create_stock("AAPL", Decimal("160.00")))
        assert pt.entry_price == Decimal("160.00")


class TestGenerateNotification:
    def test_returns_none_when_no_entry_price_set(self):
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        assert pt.generate_notification(create_stock("AAPL", Decimal("200.00"))) is None

    def test_returns_none_when_price_has_not_yet_risen_to_target(self):
        # entry=100, target=200, current=150 → target not reached
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        assert pt.generate_notification(create_stock("AAPL", Decimal("150.00"))) is None

    def test_returns_none_when_price_has_not_yet_dropped_to_target(self):
        # entry=200, target=100, current=150 → target not reached
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("100.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("200.00")))
        assert pt.generate_notification(create_stock("AAPL", Decimal("150.00"))) is None

    def test_returns_notification_when_price_rises_to_target(self):
        # entry=100, target=200, current=200 → current >= target >= entry
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        assert pt.generate_notification(create_stock("AAPL", Decimal("200.00"))) is not None

    def test_returns_notification_when_price_rises_above_target(self):
        # entry=100, target=200, current=250 → current >= target >= entry
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        assert pt.generate_notification(create_stock("AAPL", Decimal("250.00"))) is not None

    def test_returns_notification_when_price_drops_to_target(self):
        # entry=200, target=100, current=100 → current <= target <= entry
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("100.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("200.00")))
        assert pt.generate_notification(create_stock("AAPL", Decimal("100.00"))) is not None

    def test_returns_notification_when_price_drops_below_target(self):
        # entry=200, target=100, current=80 → current <= target <= entry
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("100.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("200.00")))
        assert pt.generate_notification(create_stock("AAPL", Decimal("80.00"))) is not None

    def test_returns_notification_when_current_price_equals_target_equals_entry(self):
        # entry=100, target=100, current=100 → both conditions hold
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("100.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        assert pt.generate_notification(create_stock("AAPL", Decimal("100.00"))) is not None

    def test_notification_type_is_target_price_reached(self):
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        notification = pt.generate_notification(create_stock("AAPL", Decimal("200.00")))
        assert notification.type == NotificationType.TARGET_PRICE_REACHED

    def test_notification_message_contains_symbol_and_target_price(self):
        pt = TargetPrice(symbol="AAPL", target_price=Decimal("200.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        notification = pt.generate_notification(create_stock("AAPL", Decimal("200.00")))
        assert "AAPL" in notification.message
        assert "200.00" in notification.message

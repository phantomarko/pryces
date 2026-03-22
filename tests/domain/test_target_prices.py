from decimal import Decimal

from pryces.domain.target_prices import TargetPrice
from tests.fixtures.factories import create_stock


class TestTargetPriceConstruction:
    def test_sets_target_and_entry_price(self):
        pt = TargetPrice(target=Decimal("200.00"), entry_price=Decimal("150.00"))
        assert pt.target == Decimal("200.00")
        assert pt.entry == Decimal("150.00")


class TestIsReached:
    def test_returns_false_when_price_has_not_yet_risen_to_target(self):
        # entry=100, target=200, current=150 → target not reached
        pt = TargetPrice(target=Decimal("200.00"), entry_price=Decimal("100.00"))
        assert pt.is_reached(create_stock("AAPL", Decimal("150.00"))) is False

    def test_returns_false_when_price_has_not_yet_dropped_to_target(self):
        # entry=200, target=100, current=150 → target not reached
        pt = TargetPrice(target=Decimal("100.00"), entry_price=Decimal("200.00"))
        assert pt.is_reached(create_stock("AAPL", Decimal("150.00"))) is False

    def test_returns_true_when_price_rises_to_target(self):
        # entry=100, target=200, current=200 → current >= target >= entry
        pt = TargetPrice(target=Decimal("200.00"), entry_price=Decimal("100.00"))
        assert pt.is_reached(create_stock("AAPL", Decimal("200.00"))) is True

    def test_returns_true_when_price_rises_above_target(self):
        # entry=100, target=200, current=250 → current >= target >= entry
        pt = TargetPrice(target=Decimal("200.00"), entry_price=Decimal("100.00"))
        assert pt.is_reached(create_stock("AAPL", Decimal("250.00"))) is True

    def test_returns_true_when_price_drops_to_target(self):
        # entry=200, target=100, current=100 → current <= target <= entry
        pt = TargetPrice(target=Decimal("100.00"), entry_price=Decimal("200.00"))
        assert pt.is_reached(create_stock("AAPL", Decimal("100.00"))) is True

    def test_returns_true_when_price_drops_below_target(self):
        # entry=200, target=100, current=80 → current <= target <= entry
        pt = TargetPrice(target=Decimal("100.00"), entry_price=Decimal("200.00"))
        assert pt.is_reached(create_stock("AAPL", Decimal("80.00"))) is True

    def test_returns_true_when_current_price_equals_target_equals_entry(self):
        # entry=100, target=100, current=100 → both conditions hold
        pt = TargetPrice(target=Decimal("100.00"), entry_price=Decimal("100.00"))
        assert pt.is_reached(create_stock("AAPL", Decimal("100.00"))) is True

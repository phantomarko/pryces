from decimal import Decimal

from pryces.domain.target_prices import TargetPrice
from tests.fixtures.factories import create_stock


class TestTargetPriceConstruction:
    def test_sets_symbol(self):
        pt = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        assert pt.symbol == "AAPL"

    def test_sets_target_price(self):
        pt = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        assert pt.target == Decimal("200.00")

    def test_entry_price_is_none_by_default(self):
        pt = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        assert pt.entry is None


class TestSetEntryPrice:
    def test_sets_entry_price_from_stock_current_price(self):
        pt = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        stock = create_stock("AAPL", Decimal("150.00"))
        pt.set_entry_price(stock)
        assert pt.entry == Decimal("150.00")

    def test_does_not_overwrite_existing_entry_price(self):
        pt = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("150.00")))
        pt.set_entry_price(create_stock("AAPL", Decimal("160.00")))
        assert pt.entry == Decimal("150.00")


class TestIsReached:
    def test_returns_false_when_no_entry_price_set(self):
        pt = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        assert pt.is_reached(create_stock("AAPL", Decimal("200.00"))) is False

    def test_returns_false_when_price_has_not_yet_risen_to_target(self):
        # entry=100, target=200, current=150 → target not reached
        pt = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        assert pt.is_reached(create_stock("AAPL", Decimal("150.00"))) is False

    def test_returns_false_when_price_has_not_yet_dropped_to_target(self):
        # entry=200, target=100, current=150 → target not reached
        pt = TargetPrice(symbol="AAPL", target=Decimal("100.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("200.00")))
        assert pt.is_reached(create_stock("AAPL", Decimal("150.00"))) is False

    def test_returns_true_when_price_rises_to_target(self):
        # entry=100, target=200, current=200 → current >= target >= entry
        pt = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        assert pt.is_reached(create_stock("AAPL", Decimal("200.00"))) is True

    def test_returns_true_when_price_rises_above_target(self):
        # entry=100, target=200, current=250 → current >= target >= entry
        pt = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        assert pt.is_reached(create_stock("AAPL", Decimal("250.00"))) is True

    def test_returns_true_when_price_drops_to_target(self):
        # entry=200, target=100, current=100 → current <= target <= entry
        pt = TargetPrice(symbol="AAPL", target=Decimal("100.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("200.00")))
        assert pt.is_reached(create_stock("AAPL", Decimal("100.00"))) is True

    def test_returns_true_when_price_drops_below_target(self):
        # entry=200, target=100, current=80 → current <= target <= entry
        pt = TargetPrice(symbol="AAPL", target=Decimal("100.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("200.00")))
        assert pt.is_reached(create_stock("AAPL", Decimal("80.00"))) is True

    def test_returns_true_when_current_price_equals_target_equals_entry(self):
        # entry=100, target=100, current=100 → both conditions hold
        pt = TargetPrice(symbol="AAPL", target=Decimal("100.00"))
        pt.set_entry_price(create_stock("AAPL", Decimal("100.00")))
        assert pt.is_reached(create_stock("AAPL", Decimal("100.00"))) is True

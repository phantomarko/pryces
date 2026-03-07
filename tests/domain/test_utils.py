from decimal import Decimal

import pytest

from pryces.domain.utils import _calculate_percentage_change


class TestCalculatePercentageChange:
    def test_positive_change(self):
        result = _calculate_percentage_change(Decimal("110"), Decimal("100"))
        assert result == Decimal("10")

    def test_negative_change(self):
        result = _calculate_percentage_change(Decimal("90"), Decimal("100"))
        assert result == Decimal("-10")

    def test_zero_change(self):
        result = _calculate_percentage_change(Decimal("100"), Decimal("100"))
        assert result == Decimal("0")

    def test_decimal_precision_preserved(self):
        result = _calculate_percentage_change(Decimal("105.5"), Decimal("100"))
        assert result == Decimal("5.5")

    def test_fractional_reference(self):
        result = _calculate_percentage_change(Decimal("1.5"), Decimal("1"))
        assert result == Decimal("50")

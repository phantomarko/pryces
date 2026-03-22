from decimal import Decimal

from pryces.domain.stocks import Stock


class TargetPrice:
    __slots__ = ("_target", "_entry")

    def __init__(self, target: Decimal, entry_price: Decimal) -> None:
        self._target = target
        self._entry = entry_price

    @property
    def target(self) -> Decimal:
        return self._target

    @property
    def entry(self) -> Decimal:
        return self._entry

    def is_reached(self, stock: Stock) -> bool:
        current = stock.current_price
        return current <= self._target <= self._entry or current >= self._target >= self._entry

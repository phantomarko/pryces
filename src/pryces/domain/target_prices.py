from decimal import Decimal

from pryces.domain.stocks import Stock


class TargetPrice:
    __slots__ = ("_target", "_entry")

    def __init__(self, target: Decimal) -> None:
        self._target = target
        self._entry: Decimal | None = None

    @property
    def target(self) -> Decimal:
        return self._target

    @property
    def entry(self) -> Decimal | None:
        return self._entry

    def set_entry_price(self, stock: Stock) -> None:
        if self._entry is None:
            self._entry = stock.current_price

    def is_reached(self, stock: Stock) -> bool:
        if self._entry is None:
            return False

        current = stock.current_price
        return current <= self._target <= self._entry or current >= self._target >= self._entry

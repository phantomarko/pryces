from decimal import Decimal

from pryces.domain.notifications import Notification
from pryces.domain.stocks import Stock


class TargetPrice:
    __slots__ = ("_symbol", "_target", "_entry")

    def __init__(self, symbol: str, target: Decimal) -> None:
        self._symbol = symbol
        self._target = target
        self._entry: Decimal | None = None

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def target(self) -> Decimal:
        return self._target

    @property
    def entry(self) -> Decimal | None:
        return self._entry

    def set_entry_price(self, stock: Stock) -> None:
        if self._entry is None:
            self._entry = stock.current_price

    def generate_notification(self, stock: Stock) -> Notification | None:
        return (
            Notification.create_target_price_reached(self._symbol, self._target)
            if self._is_target_reached(stock)
            else None
        )

    def _is_target_reached(self, stock: Stock) -> bool:
        if self._entry is None:
            return False

        current = stock.current_price
        return current <= self._target <= self._entry or current >= self._target >= self._entry

from decimal import Decimal

from pryces.domain.notifications import Notification
from pryces.domain.stocks import Stock


class PriceTarget:
    __slots__ = ("_symbol", "_target_price", "_entry_price")

    def __init__(self, symbol: str, target_price: Decimal) -> None:
        self._symbol = symbol
        self._target_price = target_price
        self._entry_price: Decimal | None = None

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def target_price(self) -> Decimal:
        return self._target_price

    @property
    def entry_price(self) -> Decimal | None:
        return self._entry_price

    def set_entry_price(self, stock: Stock) -> None:
        self._entry_price = stock.currentPrice

    def generate_notification(self, stock: Stock) -> Notification | None:
        return (
            Notification.create_target_price_reached(self._symbol, self._target_price)
            if self._is_target_reached(stock)
            else None
        )

    def _is_target_reached(self, stock: Stock) -> bool:
        if self._entry_price is None:
            return False

        current = stock.currentPrice
        return (
            current <= self._target_price <= self._entry_price
            or current >= self._target_price >= self._entry_price
        )

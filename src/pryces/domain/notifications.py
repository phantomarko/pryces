from decimal import Decimal
from enum import Enum


class NotificationType(Enum):
    SMA50_CROSSED = "SMA50_CROSSED"
    SMA200_CROSSED = "SMA200_CROSSED"


class Notification:
    _CREATION_KEY = object()

    def __init__(self, key: object, type: NotificationType, message: str):
        if key is not Notification._CREATION_KEY:
            raise TypeError("Use factory methods to create a Notification")
        self._type = type
        self._message = message

    @property
    def type(self) -> NotificationType:
        return self._type

    @property
    def message(self) -> str:
        return self._message

    def equals(self, other: "Notification") -> bool:
        return self._type == other._type

    @staticmethod
    def create_fifty_day_average_crossed(
        symbol: str, current_price: Decimal, average_price: Decimal
    ) -> "Notification":
        message = (
            f"{symbol} price crossed the 50-day moving average ({average_price}). "
            f"Current price: {current_price}"
        )
        return Notification(Notification._CREATION_KEY, NotificationType.SMA50_CROSSED, message)

    @staticmethod
    def create_two_hundred_day_average_crossed(
        symbol: str, current_price: Decimal, average_price: Decimal
    ) -> "Notification":
        message = (
            f"{symbol} price crossed the 200-day moving average ({average_price}). "
            f"Current price: {current_price}"
        )
        return Notification(Notification._CREATION_KEY, NotificationType.SMA200_CROSSED, message)

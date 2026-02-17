from decimal import Decimal
from enum import Enum


class NotificationType(Enum):
    SMA50_CROSSED = "SMA50_CROSSED"
    SMA200_CROSSED = "SMA200_CROSSED"
    CLOSE_TO_SMA50 = "CLOSE_TO_SMA50"
    CLOSE_TO_SMA200 = "CLOSE_TO_SMA200"
    REGULAR_MARKET_OPEN = "REGULAR_MARKET_OPEN"
    REGULAR_MARKET_CLOSED = "REGULAR_MARKET_CLOSED"
    FIVE_PERCENT_INCREASE = "FIVE_PERCENT_INCREASE"
    TEN_PERCENT_INCREASE = "TEN_PERCENT_INCREASE"
    FIFTEEN_PERCENT_INCREASE = "FIFTEEN_PERCENT_INCREASE"
    TWENTY_PERCENT_INCREASE = "TWENTY_PERCENT_INCREASE"
    FIVE_PERCENT_DECREASE = "FIVE_PERCENT_DECREASE"
    TEN_PERCENT_DECREASE = "TEN_PERCENT_DECREASE"
    FIFTEEN_PERCENT_DECREASE = "FIFTEEN_PERCENT_DECREASE"
    TWENTY_PERCENT_DECREASE = "TWENTY_PERCENT_DECREASE"


class Notification:
    __slots__ = ("_type", "_message")
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

    @staticmethod
    def create_fifty_day_average_crossed(
        symbol: str, current_price: Decimal, average_price: Decimal
    ) -> "Notification":
        message = f"{symbol} crossed SMA50 at {current_price} (SMA: {average_price})"
        return Notification(Notification._CREATION_KEY, NotificationType.SMA50_CROSSED, message)

    @staticmethod
    def create_two_hundred_day_average_crossed(
        symbol: str, current_price: Decimal, average_price: Decimal
    ) -> "Notification":
        message = f"{symbol} crossed SMA200 at {current_price} (SMA: {average_price})"
        return Notification(Notification._CREATION_KEY, NotificationType.SMA200_CROSSED, message)

    @staticmethod
    def create_close_to_fifty_day_average(
        symbol: str,
        current_price: Decimal,
        average_price: Decimal,
        change_percentage: Decimal,
    ) -> "Notification":
        message = f"{symbol} nearing SMA50 by {change_percentage:+.2f}% ({current_price} \u2192 SMA: {average_price})"
        return Notification(Notification._CREATION_KEY, NotificationType.CLOSE_TO_SMA50, message)

    @staticmethod
    def create_close_to_two_hundred_day_average(
        symbol: str,
        current_price: Decimal,
        average_price: Decimal,
        change_percentage: Decimal,
    ) -> "Notification":
        message = f"{symbol} nearing SMA200 by {change_percentage:+.2f}% ({current_price} \u2192 SMA: {average_price})"
        return Notification(Notification._CREATION_KEY, NotificationType.CLOSE_TO_SMA200, message)

    @staticmethod
    def create_regular_market_open(
        symbol: str, open_price: Decimal, last_close_price: Decimal | None
    ) -> "Notification":
        message = f"{symbol} opened at {open_price}"
        if last_close_price is not None:
            change_percentage = ((open_price - last_close_price) / last_close_price) * 100
            message += f" ({change_percentage:+.2f}%)"
        return Notification(
            Notification._CREATION_KEY, NotificationType.REGULAR_MARKET_OPEN, message
        )

    @staticmethod
    def create_regular_market_closed(
        symbol: str, current_price: Decimal, last_close_price: Decimal | None
    ) -> "Notification":
        message = f"{symbol} closed at {current_price}"
        if last_close_price is not None:
            change_percentage = ((current_price - last_close_price) / last_close_price) * 100
            message += f" ({change_percentage:+.2f}%)"
        return Notification(
            Notification._CREATION_KEY, NotificationType.REGULAR_MARKET_CLOSED, message
        )

    @staticmethod
    def create_five_percent_increase(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = f"{symbol} rose to {current_price} ({change_percentage:+.2f}%)"
        return Notification(
            Notification._CREATION_KEY, NotificationType.FIVE_PERCENT_INCREASE, message
        )

    @staticmethod
    def create_ten_percent_increase(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = f"{symbol} rose to {current_price} ({change_percentage:+.2f}%)"
        return Notification(
            Notification._CREATION_KEY, NotificationType.TEN_PERCENT_INCREASE, message
        )

    @staticmethod
    def create_fifteen_percent_increase(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = f"{symbol} rose to {current_price} ({change_percentage:+.2f}%)"
        return Notification(
            Notification._CREATION_KEY, NotificationType.FIFTEEN_PERCENT_INCREASE, message
        )

    @staticmethod
    def create_twenty_percent_increase(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = f"{symbol} rose to {current_price} ({change_percentage:+.2f}%)"
        return Notification(
            Notification._CREATION_KEY, NotificationType.TWENTY_PERCENT_INCREASE, message
        )

    @staticmethod
    def create_five_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = f"{symbol} dropped to {current_price} ({change_percentage:+.2f}%)"
        return Notification(
            Notification._CREATION_KEY, NotificationType.FIVE_PERCENT_DECREASE, message
        )

    @staticmethod
    def create_ten_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = f"{symbol} dropped to {current_price} ({change_percentage:+.2f}%)"
        return Notification(
            Notification._CREATION_KEY, NotificationType.TEN_PERCENT_DECREASE, message
        )

    @staticmethod
    def create_fifteen_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = f"{symbol} dropped to {current_price} ({change_percentage:+.2f}%)"
        return Notification(
            Notification._CREATION_KEY, NotificationType.FIFTEEN_PERCENT_DECREASE, message
        )

    @staticmethod
    def create_twenty_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = f"{symbol} dropped to {current_price} ({change_percentage:+.2f}%)"
        return Notification(
            Notification._CREATION_KEY, NotificationType.TWENTY_PERCENT_DECREASE, message
        )

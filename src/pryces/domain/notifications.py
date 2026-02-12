from decimal import Decimal
from enum import Enum


class NotificationType(Enum):
    SMA50_CROSSED = "SMA50_CROSSED"
    SMA200_CROSSED = "SMA200_CROSSED"
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
            f"{symbol} price crossed the 50-day moving average\n"
            f"SMA50: {average_price}\n"
            f"Price: {current_price}"
        )
        return Notification(Notification._CREATION_KEY, NotificationType.SMA50_CROSSED, message)

    @staticmethod
    def create_two_hundred_day_average_crossed(
        symbol: str, current_price: Decimal, average_price: Decimal
    ) -> "Notification":
        message = (
            f"{symbol} price crossed the 200-day moving average\n"
            f"SMA200: {average_price}\n"
            f"Price: {current_price}"
        )
        return Notification(Notification._CREATION_KEY, NotificationType.SMA200_CROSSED, message)

    @staticmethod
    def create_regular_market_open(
        symbol: str, open_price: Decimal, last_close_price: Decimal | None
    ) -> "Notification":
        message = f"{symbol} regular market is now open\nPrice: {open_price}"
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
        message = f"{symbol} regular market is now closed\nPrice: {current_price}"
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
        message = (
            f"{symbol} price increased more than 5% ({change_percentage:+.2f}%)\n"
            f"Price: {current_price}"
        )
        return Notification(
            Notification._CREATION_KEY, NotificationType.FIVE_PERCENT_INCREASE, message
        )

    @staticmethod
    def create_ten_percent_increase(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = (
            f"{symbol} price increased more than 10% ({change_percentage:+.2f}%)\n"
            f"Price: {current_price}"
        )
        return Notification(
            Notification._CREATION_KEY, NotificationType.TEN_PERCENT_INCREASE, message
        )

    @staticmethod
    def create_fifteen_percent_increase(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = (
            f"{symbol} price increased more than 15% ({change_percentage:+.2f}%)\n"
            f"Price: {current_price}"
        )
        return Notification(
            Notification._CREATION_KEY, NotificationType.FIFTEEN_PERCENT_INCREASE, message
        )

    @staticmethod
    def create_twenty_percent_increase(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = (
            f"{symbol} price increased more than 20% ({change_percentage:+.2f}%)\n"
            f"Price: {current_price}"
        )
        return Notification(
            Notification._CREATION_KEY, NotificationType.TWENTY_PERCENT_INCREASE, message
        )

    @staticmethod
    def create_five_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = (
            f"{symbol} price decreased more than 5% ({change_percentage:+.2f}%)\n"
            f"Price: {current_price}"
        )
        return Notification(
            Notification._CREATION_KEY, NotificationType.FIVE_PERCENT_DECREASE, message
        )

    @staticmethod
    def create_ten_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = (
            f"{symbol} price decreased more than 10% ({change_percentage:+.2f}%)\n"
            f"Price: {current_price}"
        )
        return Notification(
            Notification._CREATION_KEY, NotificationType.TEN_PERCENT_DECREASE, message
        )

    @staticmethod
    def create_fifteen_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = (
            f"{symbol} price decreased more than 15% ({change_percentage:+.2f}%)\n"
            f"Price: {current_price}"
        )
        return Notification(
            Notification._CREATION_KEY, NotificationType.FIFTEEN_PERCENT_DECREASE, message
        )

    @staticmethod
    def create_twenty_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        message = (
            f"{symbol} price decreased more than 20% ({change_percentage:+.2f}%)\n"
            f"Price: {current_price}"
        )
        return Notification(
            Notification._CREATION_KEY, NotificationType.TWENTY_PERCENT_DECREASE, message
        )

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
    NEW_52_WEEK_HIGH = "NEW_52_WEEK_HIGH"
    NEW_52_WEEK_LOW = "NEW_52_WEEK_LOW"
    TARGET_PRICE_REACHED = "TARGET_PRICE_REACHED"


class Notification:
    __slots__ = ("_type", "_message")
    _CREATION_KEY = object()

    def __init__(self, key: object, notification_type: NotificationType, message: str):
        if key is not Notification._CREATION_KEY:
            raise TypeError("Use factory methods to create a Notification")
        self._type = notification_type
        self._message = message

    @property
    def type(self) -> NotificationType:
        return self._type

    @property
    def message(self) -> str:
        return self._message

    @staticmethod
    def create_fifty_day_average_crossed(
        symbol: str,
        current_price: Decimal,
        change_percentage: Decimal,
        average_price: Decimal,
    ) -> "Notification":
        prefix = Notification._format_price_change_prefix(symbol, current_price, change_percentage)
        message = f"{prefix}, crossed SMA50 at {average_price}"
        return Notification(Notification._CREATION_KEY, NotificationType.SMA50_CROSSED, message)

    @staticmethod
    def create_two_hundred_day_average_crossed(
        symbol: str,
        current_price: Decimal,
        change_percentage: Decimal,
        average_price: Decimal,
    ) -> "Notification":
        prefix = Notification._format_price_change_prefix(symbol, current_price, change_percentage)
        message = f"{prefix}, crossed SMA200 at {average_price}"
        return Notification(Notification._CREATION_KEY, NotificationType.SMA200_CROSSED, message)

    @staticmethod
    def create_close_to_fifty_day_average(
        symbol: str,
        current_price: Decimal,
        change_percentage: Decimal,
        average_price: Decimal,
    ) -> "Notification":
        prefix = Notification._format_price_change_prefix(symbol, current_price, change_percentage)
        direction = "above" if current_price >= average_price else "below"
        message = f"{prefix}, {direction} SMA50 at {average_price}"
        return Notification(Notification._CREATION_KEY, NotificationType.CLOSE_TO_SMA50, message)

    @staticmethod
    def create_close_to_two_hundred_day_average(
        symbol: str,
        current_price: Decimal,
        change_percentage: Decimal,
        average_price: Decimal,
    ) -> "Notification":
        prefix = Notification._format_price_change_prefix(symbol, current_price, change_percentage)
        direction = "above" if current_price >= average_price else "below"
        message = f"{prefix}, {direction} SMA200 at {average_price}"
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
        return Notification._create_price_change(
            NotificationType.FIVE_PERCENT_INCREASE,
            symbol,
            current_price,
            change_percentage,
        )

    @staticmethod
    def create_ten_percent_increase(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        return Notification._create_price_change(
            NotificationType.TEN_PERCENT_INCREASE,
            symbol,
            current_price,
            change_percentage,
        )

    @staticmethod
    def create_fifteen_percent_increase(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        return Notification._create_price_change(
            NotificationType.FIFTEEN_PERCENT_INCREASE,
            symbol,
            current_price,
            change_percentage,
        )

    @staticmethod
    def create_twenty_percent_increase(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        return Notification._create_price_change(
            NotificationType.TWENTY_PERCENT_INCREASE,
            symbol,
            current_price,
            change_percentage,
        )

    @staticmethod
    def create_five_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        return Notification._create_price_change(
            NotificationType.FIVE_PERCENT_DECREASE,
            symbol,
            current_price,
            change_percentage,
        )

    @staticmethod
    def create_ten_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        return Notification._create_price_change(
            NotificationType.TEN_PERCENT_DECREASE,
            symbol,
            current_price,
            change_percentage,
        )

    @staticmethod
    def create_fifteen_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        return Notification._create_price_change(
            NotificationType.FIFTEEN_PERCENT_DECREASE,
            symbol,
            current_price,
            change_percentage,
        )

    @staticmethod
    def create_twenty_percent_decrease(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> "Notification":
        return Notification._create_price_change(
            NotificationType.TWENTY_PERCENT_DECREASE,
            symbol,
            current_price,
            change_percentage,
        )

    @staticmethod
    def _format_price_change_prefix(
        symbol: str, current_price: Decimal, change_percentage: Decimal
    ) -> str:
        verb = "rose to" if change_percentage >= 0 else "dropped to"
        return f"{symbol} {verb} {current_price} ({change_percentage:+.2f}%)"

    @staticmethod
    def _create_price_change(
        notification_type: NotificationType,
        symbol: str,
        current_price: Decimal,
        change_percentage: Decimal,
    ) -> "Notification":
        message = Notification._format_price_change_prefix(symbol, current_price, change_percentage)
        return Notification(Notification._CREATION_KEY, notification_type, message)

    @staticmethod
    def create_new_52_week_high(symbol: str, current_price: Decimal) -> "Notification":
        message = f"{symbol} hit a new 52-week high at {current_price}"
        return Notification(Notification._CREATION_KEY, NotificationType.NEW_52_WEEK_HIGH, message)

    @staticmethod
    def create_new_52_week_low(symbol: str, current_price: Decimal) -> "Notification":
        message = f"{symbol} hit a new 52-week low at {current_price}"
        return Notification(Notification._CREATION_KEY, NotificationType.NEW_52_WEEK_LOW, message)

    @staticmethod
    def create_target_price_reached(symbol: str, target_price: Decimal) -> "Notification":
        message = f"{symbol} hit target of {target_price}"
        return Notification(
            Notification._CREATION_KEY, NotificationType.TARGET_PRICE_REACHED, message
        )

from decimal import Decimal
from enum import Enum

from pryces.domain.notifications import Notification, NotificationType


class MarketState(str, Enum):
    OPEN = "OPEN"
    PRE = "PRE"
    POST = "POST"
    CLOSED = "CLOSED"


class Stock:
    __slots__ = (
        "_symbol",
        "_currentPrice",
        "_name",
        "_currency",
        "_previousClosePrice",
        "_openPrice",
        "_dayHigh",
        "_dayLow",
        "_fiftyDayAverage",
        "_twoHundredDayAverage",
        "_fiftyTwoWeekHigh",
        "_fiftyTwoWeekLow",
        "_marketState",
        "_priceDelayInMinutes",
        "_notifications",
    )

    def __init__(
        self,
        *,
        symbol: str,
        currentPrice: Decimal,
        name: str | None = None,
        currency: str | None = None,
        previousClosePrice: Decimal | None = None,
        openPrice: Decimal | None = None,
        dayHigh: Decimal | None = None,
        dayLow: Decimal | None = None,
        fiftyDayAverage: Decimal | None = None,
        twoHundredDayAverage: Decimal | None = None,
        fiftyTwoWeekHigh: Decimal | None = None,
        fiftyTwoWeekLow: Decimal | None = None,
        marketState: MarketState | None = None,
        priceDelayInMinutes: int | None = None,
    ):
        self._symbol = symbol
        self._currentPrice = currentPrice
        self._name = name
        self._currency = currency
        self._previousClosePrice = previousClosePrice
        self._openPrice = openPrice
        self._dayHigh = dayHigh
        self._dayLow = dayLow
        self._fiftyDayAverage = fiftyDayAverage
        self._twoHundredDayAverage = twoHundredDayAverage
        self._fiftyTwoWeekHigh = fiftyTwoWeekHigh
        self._fiftyTwoWeekLow = fiftyTwoWeekLow
        self._marketState = marketState
        self._priceDelayInMinutes = priceDelayInMinutes
        self._notifications: list[Notification] = []

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def currentPrice(self) -> Decimal:
        return self._currentPrice

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def currency(self) -> str | None:
        return self._currency

    @property
    def previousClosePrice(self) -> Decimal | None:
        return self._previousClosePrice

    @property
    def openPrice(self) -> Decimal | None:
        return self._openPrice

    @property
    def dayHigh(self) -> Decimal | None:
        return self._dayHigh

    @property
    def dayLow(self) -> Decimal | None:
        return self._dayLow

    @property
    def fiftyDayAverage(self) -> Decimal | None:
        return self._fiftyDayAverage

    @property
    def twoHundredDayAverage(self) -> Decimal | None:
        return self._twoHundredDayAverage

    @property
    def fiftyTwoWeekHigh(self) -> Decimal | None:
        return self._fiftyTwoWeekHigh

    @property
    def fiftyTwoWeekLow(self) -> Decimal | None:
        return self._fiftyTwoWeekLow

    @property
    def marketState(self) -> MarketState | None:
        return self._marketState

    @property
    def priceDelayInMinutes(self) -> int | None:
        return self._priceDelayInMinutes

    @property
    def notifications(self) -> list[Notification]:
        return self._notifications

    def _is_close_to_fifty_day_average(self) -> bool:
        if self.fiftyDayAverage is None or self.previousClosePrice is None:
            return False

        change_percentage = (self.fiftyDayAverage - self.currentPrice) / self.currentPrice * 100

        return (
            self.previousClosePrice < self.fiftyDayAverage
            and self.currentPrice < self.fiftyDayAverage
            and change_percentage <= self._CLOSE_TO_SMA_UPPER_THRESHOLD
        ) or (
            self.previousClosePrice > self.fiftyDayAverage
            and self.currentPrice > self.fiftyDayAverage
            and change_percentage >= self._CLOSE_TO_SMA_LOWER_THRESHOLD
        )

    def _has_crossed_fifty_day_average(self) -> bool:
        if self.previousClosePrice is None or self.fiftyDayAverage is None:
            return False

        crossed_above = (
            self.previousClosePrice < self.fiftyDayAverage
            and self.currentPrice >= self.fiftyDayAverage
        )
        crossed_below = (
            self.previousClosePrice > self.fiftyDayAverage
            and self.currentPrice <= self.fiftyDayAverage
        )

        return crossed_above or crossed_below

    def _is_close_to_two_hundred_day_average(self) -> bool:
        if self.twoHundredDayAverage is None or self.previousClosePrice is None:
            return False

        change_percentage = (
            (self.twoHundredDayAverage - self.currentPrice) / self.currentPrice * 100
        )

        return (
            self.previousClosePrice < self.twoHundredDayAverage
            and self.currentPrice < self.twoHundredDayAverage
            and change_percentage <= self._CLOSE_TO_SMA_UPPER_THRESHOLD
        ) or (
            self.previousClosePrice > self.twoHundredDayAverage
            and self.currentPrice > self.twoHundredDayAverage
            and change_percentage >= self._CLOSE_TO_SMA_LOWER_THRESHOLD
        )

    def _has_crossed_two_hundred_day_average(self) -> bool:
        if self.previousClosePrice is None or self.twoHundredDayAverage is None:
            return False

        crossed_above = (
            self.previousClosePrice < self.twoHundredDayAverage
            and self.currentPrice >= self.twoHundredDayAverage
        )
        crossed_below = (
            self.previousClosePrice > self.twoHundredDayAverage
            and self.currentPrice <= self.twoHundredDayAverage
        )

        return crossed_above or crossed_below

    def _change_percentage_from_previous_close(self) -> Decimal | None:
        if self.previousClosePrice is None:
            return None

        return (self.currentPrice - self.previousClosePrice) / self.previousClosePrice * 100

    def _is_market_state_open(self) -> bool:
        return self._marketState == MarketState.OPEN

    def _is_market_state_post(self) -> bool:
        return self._marketState == MarketState.POST

    _CLOSE_TO_SMA_UPPER_THRESHOLD = Decimal("5")
    _CLOSE_TO_SMA_LOWER_THRESHOLD = Decimal("-5")

    _INCREASE_THRESHOLDS = (
        (Decimal("20"), Notification.create_twenty_percent_increase),
        (Decimal("15"), Notification.create_fifteen_percent_increase),
        (Decimal("10"), Notification.create_ten_percent_increase),
        (Decimal("5"), Notification.create_five_percent_increase),
    )
    _DECREASE_THRESHOLDS = (
        (Decimal("-20"), Notification.create_twenty_percent_decrease),
        (Decimal("-15"), Notification.create_fifteen_percent_decrease),
        (Decimal("-10"), Notification.create_ten_percent_decrease),
        (Decimal("-5"), Notification.create_five_percent_decrease),
    )

    def _generate_percentage_change_notification(
        self, change_percentage: Decimal
    ) -> Notification | None:
        args = (self.symbol, self.currentPrice, change_percentage)

        if change_percentage > 0:
            for threshold, factory in self._INCREASE_THRESHOLDS:
                if change_percentage >= threshold:
                    return factory(*args)
        elif change_percentage < 0:
            for threshold, factory in self._DECREASE_THRESHOLDS:
                if change_percentage <= threshold:
                    return factory(*args)

        return None

    def _generate_new_52_week_high_notification(self, past_stock: "Stock | None") -> None:
        if (
            past_stock is not None
            and past_stock.fiftyTwoWeekHigh is not None
            and self.currentPrice > past_stock.fiftyTwoWeekHigh
        ):
            self._notifications.append(
                Notification.create_new_52_week_high(self.symbol, self.currentPrice)
            )

    def _generate_new_52_week_low_notification(self, past_stock: "Stock | None") -> None:
        if (
            past_stock is not None
            and past_stock.fiftyTwoWeekLow is not None
            and self.currentPrice < past_stock.fiftyTwoWeekLow
        ):
            self._notifications.append(
                Notification.create_new_52_week_low(self.symbol, self.currentPrice)
            )

    def _generate_regular_market_open_notification(self) -> None:
        self._notifications.append(
            Notification.create_regular_market_open(
                self.symbol,
                self.openPrice if self.openPrice is not None else self.currentPrice,
                self.previousClosePrice,
            )
        )

    def _generate_close_to_fifty_day_average_notification(self) -> None:
        if self._is_close_to_fifty_day_average():
            change_pct = (self.fiftyDayAverage - self.currentPrice) / self.currentPrice * 100
            self._notifications.append(
                Notification.create_close_to_fifty_day_average(
                    self.symbol, self.currentPrice, self.fiftyDayAverage, change_pct
                )
            )

    def _generate_fifty_day_average_crossed_notification(self) -> None:
        if self._has_crossed_fifty_day_average():
            self._notifications.append(
                Notification.create_fifty_day_average_crossed(
                    self.symbol, self.currentPrice, self.fiftyDayAverage
                )
            )

    def _generate_close_to_two_hundred_day_average_notification(self) -> None:
        if self._is_close_to_two_hundred_day_average():
            change_pct = (self.twoHundredDayAverage - self.currentPrice) / self.currentPrice * 100
            self._notifications.append(
                Notification.create_close_to_two_hundred_day_average(
                    self.symbol, self.currentPrice, self.twoHundredDayAverage, change_pct
                )
            )

    def _generate_two_hundred_day_average_crossed_notification(self) -> None:
        if self._has_crossed_two_hundred_day_average():
            self._notifications.append(
                Notification.create_two_hundred_day_average_crossed(
                    self.symbol, self.currentPrice, self.twoHundredDayAverage
                )
            )

    def _generate_percentage_change_from_previous_close_notification(self) -> None:
        change_percentage = self._change_percentage_from_previous_close()
        if change_percentage is None:
            return
        notification = self._generate_percentage_change_notification(change_percentage)
        if notification is not None:
            self._notifications.append(notification)

    def _generate_market_open_notifications(self, past_stock: "Stock | None") -> None:
        self._generate_regular_market_open_notification()
        self._generate_close_to_fifty_day_average_notification()
        self._generate_fifty_day_average_crossed_notification()
        self._generate_close_to_two_hundred_day_average_notification()
        self._generate_two_hundred_day_average_crossed_notification()
        self._generate_percentage_change_from_previous_close_notification()
        self._generate_new_52_week_high_notification(past_stock)
        self._generate_new_52_week_low_notification(past_stock)

    def _generate_regular_market_closed_notification(self) -> None:
        self._notifications.append(
            Notification.create_regular_market_closed(
                self.symbol, self.currentPrice, self.previousClosePrice
            )
        )

    def _generate_market_closed_notifications(self) -> None:
        self._generate_regular_market_closed_notification()

    def generate_notifications(self, past_stock: "Stock | None" = None) -> None:
        if self._is_market_state_open():
            self._generate_market_open_notifications(past_stock)
        elif self._is_market_state_post():
            self._generate_market_closed_notifications()

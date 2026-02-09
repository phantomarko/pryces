from decimal import Decimal
from enum import Enum

from pryces.domain.notifications import Notification, NotificationType


class MarketState(str, Enum):
    OPEN = "OPEN"
    PRE = "PRE"
    POST = "POST"
    CLOSED = "CLOSED"


class Stock:
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
    def notifications(self) -> list[Notification]:
        return self._notifications

    def has_crossed_fifty_day_average(self) -> bool:
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

    def has_crossed_two_hundred_day_average(self) -> bool:
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

    def change_percentage_from_previous_close(self) -> Decimal | None:
        if self.previousClosePrice is None:
            return None

        return (self.currentPrice - self.previousClosePrice) / self.previousClosePrice * 100

    def is_market_state_open(self) -> bool:
        return self._marketState == MarketState.OPEN

    def is_market_state_post(self) -> bool:
        return self._marketState == MarketState.POST

    def _generate_percentage_change_notification(
        self, change_percentage: Decimal
    ) -> Notification | None:
        args = (self.symbol, self.currentPrice, self.previousClosePrice, change_percentage)

        if change_percentage > 0:
            thresholds = (
                (Decimal("20"), Notification.create_twenty_percent_increase),
                (Decimal("15"), Notification.create_fifteen_percent_increase),
                (Decimal("10"), Notification.create_ten_percent_increase),
                (Decimal("5"), Notification.create_five_percent_increase),
            )
            for threshold, factory in thresholds:
                if change_percentage >= threshold:
                    return factory(*args)
        elif change_percentage < 0:
            thresholds = (
                (Decimal("-20"), Notification.create_twenty_percent_decrease),
                (Decimal("-15"), Notification.create_fifteen_percent_decrease),
                (Decimal("-10"), Notification.create_ten_percent_decrease),
                (Decimal("-5"), Notification.create_five_percent_decrease),
            )
            for threshold, factory in thresholds:
                if change_percentage <= threshold:
                    return factory(*args)

        return None

    def generate_milestones_notifications(self) -> None:
        if self.is_market_state_open():
            self._notifications.append(
                Notification.create_regular_market_open(
                    self.symbol,
                    self.openPrice if self.openPrice is not None else self.currentPrice,
                    self.previousClosePrice,
                )
            )
            if self.has_crossed_fifty_day_average():
                self._notifications.append(
                    Notification.create_fifty_day_average_crossed(
                        self.symbol, self.currentPrice, self.fiftyDayAverage
                    )
                )
            if self.has_crossed_two_hundred_day_average():
                self._notifications.append(
                    Notification.create_two_hundred_day_average_crossed(
                        self.symbol, self.currentPrice, self.twoHundredDayAverage
                    )
                )
            change_percentage = self.change_percentage_from_previous_close()
            if change_percentage is not None:
                percentage_notification = self._generate_percentage_change_notification(
                    change_percentage
                )
                if percentage_notification is not None:
                    self._notifications.append(percentage_notification)
        elif self.is_market_state_post():
            self._notifications.append(
                Notification.create_regular_market_closed(
                    self.symbol, self.currentPrice, self.openPrice
                )
            )

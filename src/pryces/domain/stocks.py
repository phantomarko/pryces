from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from pryces.domain.notifications import Notification, NotificationType

if TYPE_CHECKING:
    from pryces.domain.target_prices import TargetPrice


@dataclass(frozen=True, slots=True)
class StockSnapshot:
    current_price: Decimal
    previous_close_price: Decimal | None
    open_price: Decimal | None
    day_high: Decimal | None
    day_low: Decimal | None
    fifty_day_average: Decimal | None
    two_hundred_day_average: Decimal | None
    fifty_two_week_high: Decimal | None
    fifty_two_week_low: Decimal | None
    market_state: "MarketState | None"
    price_delay_in_minutes: int | None


class MarketState(str, Enum):
    OPEN = "OPEN"
    PRE = "PRE"
    POST = "POST"
    CLOSED = "CLOSED"


class Stock:
    __slots__ = (
        "_symbol",
        "_current_price",
        "_name",
        "_currency",
        "_previous_close_price",
        "_open_price",
        "_day_high",
        "_day_low",
        "_fifty_day_average",
        "_two_hundred_day_average",
        "_fifty_two_week_high",
        "_fifty_two_week_low",
        "_market_state",
        "_price_delay_in_minutes",
        "_snapshot",
        "_notifications",
        "_targets",
        "_fulfilled_targets",
    )

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

    def __init__(
        self,
        *,
        symbol: str,
        current_price: Decimal,
        name: str | None = None,
        currency: str | None = None,
        previous_close_price: Decimal | None = None,
        open_price: Decimal | None = None,
        day_high: Decimal | None = None,
        day_low: Decimal | None = None,
        fifty_day_average: Decimal | None = None,
        two_hundred_day_average: Decimal | None = None,
        fifty_two_week_high: Decimal | None = None,
        fifty_two_week_low: Decimal | None = None,
        market_state: MarketState | None = None,
        price_delay_in_minutes: int | None = None,
    ):
        self._symbol = symbol
        self._current_price = current_price
        self._name = name
        self._currency = currency
        self._previous_close_price = previous_close_price
        self._open_price = open_price
        self._day_high = day_high
        self._day_low = day_low
        self._fifty_day_average = fifty_day_average
        self._two_hundred_day_average = two_hundred_day_average
        self._fifty_two_week_high = fifty_two_week_high
        self._fifty_two_week_low = fifty_two_week_low
        self._market_state = market_state
        self._price_delay_in_minutes = price_delay_in_minutes
        self._snapshot: StockSnapshot | None = None
        self._notifications: list[Notification] = []
        self._targets: list[TargetPrice] = []
        self._fulfilled_targets: list[TargetPrice] = []

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def current_price(self) -> Decimal:
        return self._current_price

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def currency(self) -> str | None:
        return self._currency

    @property
    def previous_close_price(self) -> Decimal | None:
        return self._previous_close_price

    @property
    def open_price(self) -> Decimal | None:
        return self._open_price

    @property
    def day_high(self) -> Decimal | None:
        return self._day_high

    @property
    def day_low(self) -> Decimal | None:
        return self._day_low

    @property
    def fifty_day_average(self) -> Decimal | None:
        return self._fifty_day_average

    @property
    def two_hundred_day_average(self) -> Decimal | None:
        return self._two_hundred_day_average

    @property
    def fifty_two_week_high(self) -> Decimal | None:
        return self._fifty_two_week_high

    @property
    def fifty_two_week_low(self) -> Decimal | None:
        return self._fifty_two_week_low

    @property
    def market_state(self) -> MarketState | None:
        return self._market_state

    @property
    def price_delay_in_minutes(self) -> int | None:
        return self._price_delay_in_minutes

    @property
    def snapshot(self) -> StockSnapshot | None:
        return self._snapshot

    def drain_fulfilled_targets(self) -> list[Decimal]:
        fulfilled = [t.target for t in self._fulfilled_targets]
        self._fulfilled_targets = []
        return fulfilled

    def sync_targets(self, target_values: list[Decimal]) -> None:
        from pryces.domain.target_prices import TargetPrice

        existing_by_value = {t.target: t for t in self._targets}

        synced: list[TargetPrice] = []
        for value in target_values:
            existing = existing_by_value.get(value)
            if existing is not None:
                synced.append(existing)
            else:
                target = TargetPrice(value)
                target.set_entry_price(self)
                synced.append(target)

        self._targets = synced

    def update(self, source: "Stock") -> None:
        self._snapshot = self._capture_snapshot()
        self._current_price = source._current_price
        self._name = source._name
        self._currency = source._currency
        self._previous_close_price = source._previous_close_price
        self._open_price = source._open_price
        self._day_high = source._day_high
        self._day_low = source._day_low
        self._fifty_day_average = source._fifty_day_average
        self._two_hundred_day_average = source._two_hundred_day_average
        self._fifty_two_week_high = source._fifty_two_week_high
        self._fifty_two_week_low = source._fifty_two_week_low
        self._market_state = source._market_state
        self._price_delay_in_minutes = source._price_delay_in_minutes

    def is_market_state_transition(self) -> bool:
        return (
            self._snapshot is not None
            and self._snapshot.market_state != self._market_state
            and self._market_state in (MarketState.OPEN, MarketState.POST)
        )

    def generate_notifications(self) -> list[str]:
        previous_count = len(self._notifications)
        if self._is_market_state_open():
            self._generate_market_open_notifications()
        elif self._is_market_state_post():
            self._generate_market_closed_notifications()
        return [n.message for n in self._notifications[previous_count:]]

    def _capture_snapshot(self) -> StockSnapshot:
        return StockSnapshot(
            current_price=self._current_price,
            previous_close_price=self._previous_close_price,
            open_price=self._open_price,
            day_high=self._day_high,
            day_low=self._day_low,
            fifty_day_average=self._fifty_day_average,
            two_hundred_day_average=self._two_hundred_day_average,
            fifty_two_week_high=self._fifty_two_week_high,
            fifty_two_week_low=self._fifty_two_week_low,
            market_state=self._market_state,
            price_delay_in_minutes=self._price_delay_in_minutes,
        )

    def _has_notification_type(self, notification_type: NotificationType) -> bool:
        return any(n.type == notification_type for n in self._notifications)

    def _is_close_to_sma(self, sma: Decimal | None) -> bool:
        if sma is None or self.previous_close_price is None:
            return False

        change_percentage = (sma - self.current_price) / self.current_price * 100

        return (
            self.previous_close_price < sma
            and self.current_price < sma
            and change_percentage <= self._CLOSE_TO_SMA_UPPER_THRESHOLD
        ) or (
            self.previous_close_price > sma
            and self.current_price > sma
            and change_percentage >= self._CLOSE_TO_SMA_LOWER_THRESHOLD
        )

    def _has_crossed_sma(self, sma: Decimal | None) -> bool:
        if self.previous_close_price is None or sma is None:
            return False

        crossed_above = self.previous_close_price < sma and self.current_price >= sma
        crossed_below = self.previous_close_price > sma and self.current_price <= sma

        return crossed_above or crossed_below

    def _change_percentage_from_previous_close(self) -> Decimal | None:
        if self.previous_close_price is None:
            return None

        return (self.current_price - self.previous_close_price) / self.previous_close_price * 100

    def _is_market_state_open(self) -> bool:
        return self._market_state == MarketState.OPEN

    def _is_market_state_post(self) -> bool:
        return self._market_state == MarketState.POST

    def _generate_percentage_change_notification(
        self, change_percentage: Decimal
    ) -> Notification | None:
        args = (self.symbol, self.current_price, change_percentage)

        if change_percentage > 0:
            for threshold, factory in self._INCREASE_THRESHOLDS:
                if change_percentage >= threshold:
                    return factory(*args)
        elif change_percentage < 0:
            for threshold, factory in self._DECREASE_THRESHOLDS:
                if change_percentage <= threshold:
                    return factory(*args)

        return None

    def _generate_new_52_week_high_notification(self) -> None:
        if (
            self._snapshot is not None
            and self._snapshot.fifty_two_week_high is not None
            and self.current_price > self._snapshot.fifty_two_week_high
            and not self._has_notification_type(NotificationType.NEW_52_WEEK_HIGH)
        ):
            self._notifications.append(
                Notification.create_new_52_week_high(self.symbol, self.current_price)
            )

    def _generate_new_52_week_low_notification(self) -> None:
        if (
            self._snapshot is not None
            and self._snapshot.fifty_two_week_low is not None
            and self.current_price < self._snapshot.fifty_two_week_low
            and not self._has_notification_type(NotificationType.NEW_52_WEEK_LOW)
        ):
            self._notifications.append(
                Notification.create_new_52_week_low(self.symbol, self.current_price)
            )

    def _generate_regular_market_open_notification(self) -> None:
        if self._has_notification_type(NotificationType.REGULAR_MARKET_OPEN):
            return
        self._notifications.append(
            Notification.create_regular_market_open(
                self.symbol,
                self.open_price if self.open_price is not None else self.current_price,
                self.previous_close_price,
            )
        )

    def _generate_close_to_fifty_day_average_notification(self) -> None:
        if self._is_close_to_sma(self.fifty_day_average) and not self._has_notification_type(
            NotificationType.CLOSE_TO_SMA50
        ):
            change_pct = self._change_percentage_from_previous_close()
            if change_pct is None:
                return
            self._notifications.append(
                Notification.create_close_to_fifty_day_average(
                    self.symbol, self.current_price, change_pct, self.fifty_day_average
                )
            )

    def _generate_fifty_day_average_crossed_notification(self) -> None:
        if self._has_crossed_sma(self.fifty_day_average) and not self._has_notification_type(
            NotificationType.SMA50_CROSSED
        ):
            change_pct = self._change_percentage_from_previous_close()
            if change_pct is None:
                return
            self._notifications.append(
                Notification.create_fifty_day_average_crossed(
                    self.symbol, self.current_price, change_pct, self.fifty_day_average
                )
            )

    def _generate_close_to_two_hundred_day_average_notification(self) -> None:
        if self._is_close_to_sma(self.two_hundred_day_average) and not self._has_notification_type(
            NotificationType.CLOSE_TO_SMA200
        ):
            change_pct = self._change_percentage_from_previous_close()
            if change_pct is None:
                return
            self._notifications.append(
                Notification.create_close_to_two_hundred_day_average(
                    self.symbol, self.current_price, change_pct, self.two_hundred_day_average
                )
            )

    def _generate_two_hundred_day_average_crossed_notification(self) -> None:
        if self._has_crossed_sma(self.two_hundred_day_average) and not self._has_notification_type(
            NotificationType.SMA200_CROSSED
        ):
            change_pct = self._change_percentage_from_previous_close()
            if change_pct is None:
                return
            self._notifications.append(
                Notification.create_two_hundred_day_average_crossed(
                    self.symbol, self.current_price, change_pct, self.two_hundred_day_average
                )
            )

    def _generate_percentage_change_from_previous_close_notification(self) -> None:
        change_percentage = self._change_percentage_from_previous_close()
        if change_percentage is None:
            return
        notification = self._generate_percentage_change_notification(change_percentage)
        if notification is not None and not self._has_notification_type(notification.type):
            self._notifications.append(notification)

    def _generate_target_price_notifications(self) -> None:
        remaining: list[TargetPrice] = []
        for target in self._targets:
            if target.is_reached(self):
                self._notifications.append(
                    Notification.create_target_price_reached(self._symbol, target.target)
                )
                self._fulfilled_targets.append(target)
            else:
                remaining.append(target)
        self._targets = remaining

    def _generate_market_open_notifications(self) -> None:
        had_market_open = self._has_notification_type(NotificationType.REGULAR_MARKET_OPEN)
        self._generate_regular_market_open_notification()
        if not had_market_open:
            return
        self._generate_close_to_fifty_day_average_notification()
        self._generate_fifty_day_average_crossed_notification()
        self._generate_close_to_two_hundred_day_average_notification()
        self._generate_two_hundred_day_average_crossed_notification()
        self._generate_percentage_change_from_previous_close_notification()
        self._generate_new_52_week_high_notification()
        self._generate_new_52_week_low_notification()
        self._generate_target_price_notifications()

    def _generate_regular_market_closed_notification(self) -> None:
        if self._has_notification_type(NotificationType.REGULAR_MARKET_CLOSED):
            return
        self._notifications.append(
            Notification.create_regular_market_closed(
                self.symbol, self.current_price, self.previous_close_price
            )
        )

    def _generate_market_closed_notifications(self) -> None:
        self._generate_regular_market_closed_notification()

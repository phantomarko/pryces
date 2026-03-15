from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from pryces.domain.notifications import Notification, NotificationType
from pryces.domain.utils import _calculate_percentage_change

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


class InstrumentType(str, Enum):
    STOCK = "STOCK"
    ETF = "ETF"
    CRYPTO = "CRYPTO"
    INDEX = "INDEX"


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
        "_kind",
        "_snapshot",
        "_notifications",
        "_pending_notifications",
        "_targets",
        "_fulfilled_targets",
    )

    _CLOSE_TO_SMA_THRESHOLD = Decimal("2.5")

    _STOCK_INCREASE_THRESHOLDS = (
        (Decimal("20"), NotificationType.LEVEL_5_INCREASE),
        (Decimal("16"), NotificationType.LEVEL_4_INCREASE),
        (Decimal("12"), NotificationType.LEVEL_3_INCREASE),
        (Decimal("8"), NotificationType.LEVEL_2_INCREASE),
        (Decimal("4"), NotificationType.LEVEL_1_INCREASE),
    )
    _STOCK_DECREASE_THRESHOLDS = (
        (Decimal("-20"), NotificationType.LEVEL_5_DECREASE),
        (Decimal("-16"), NotificationType.LEVEL_4_DECREASE),
        (Decimal("-12"), NotificationType.LEVEL_3_DECREASE),
        (Decimal("-8"), NotificationType.LEVEL_2_DECREASE),
        (Decimal("-4"), NotificationType.LEVEL_1_DECREASE),
    )
    _CRYPTO_INCREASE_THRESHOLDS = (
        (Decimal("10"), NotificationType.LEVEL_5_INCREASE),
        (Decimal("8"), NotificationType.LEVEL_4_INCREASE),
        (Decimal("6"), NotificationType.LEVEL_3_INCREASE),
        (Decimal("4"), NotificationType.LEVEL_2_INCREASE),
        (Decimal("2"), NotificationType.LEVEL_1_INCREASE),
    )
    _CRYPTO_DECREASE_THRESHOLDS = (
        (Decimal("-10"), NotificationType.LEVEL_5_DECREASE),
        (Decimal("-8"), NotificationType.LEVEL_4_DECREASE),
        (Decimal("-6"), NotificationType.LEVEL_3_DECREASE),
        (Decimal("-4"), NotificationType.LEVEL_2_DECREASE),
        (Decimal("-2"), NotificationType.LEVEL_1_DECREASE),
    )
    _DEFAULT_INCREASE_THRESHOLDS = (
        (Decimal("3.75"), NotificationType.LEVEL_5_INCREASE),
        (Decimal("3"), NotificationType.LEVEL_4_INCREASE),
        (Decimal("2.25"), NotificationType.LEVEL_3_INCREASE),
        (Decimal("1.5"), NotificationType.LEVEL_2_INCREASE),
        (Decimal("0.75"), NotificationType.LEVEL_1_INCREASE),
    )
    _DEFAULT_DECREASE_THRESHOLDS = (
        (Decimal("-3.75"), NotificationType.LEVEL_5_DECREASE),
        (Decimal("-3"), NotificationType.LEVEL_4_DECREASE),
        (Decimal("-2.25"), NotificationType.LEVEL_3_DECREASE),
        (Decimal("-1.5"), NotificationType.LEVEL_2_DECREASE),
        (Decimal("-0.75"), NotificationType.LEVEL_1_DECREASE),
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
        kind: InstrumentType | None = None,
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
        self._kind = kind
        self._snapshot: StockSnapshot | None = None
        self._notifications: list[Notification] = []
        self._pending_notifications: list[Notification] = []
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
    def kind(self) -> "InstrumentType | None":
        return self._kind

    @property
    def snapshot(self) -> StockSnapshot | None:
        return self._snapshot

    def drain_fulfilled_targets(self) -> list[Decimal]:
        fulfilled = [t.target for t in self._fulfilled_targets]
        self._fulfilled_targets = []
        return fulfilled

    def drain_notifications(self) -> list[str]:
        messages = [n.message for n in self._pending_notifications]
        self._notifications.extend(self._pending_notifications)
        self._pending_notifications = []
        return messages

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
        self._kind = source._kind

    def is_market_state_transition(self) -> bool:
        return (
            self._snapshot is not None
            and self._snapshot.market_state != self._market_state
            and self._market_state in (MarketState.OPEN, MarketState.POST)
        )

    def generate_notifications(self) -> None:
        if self._is_market_state_open():
            self._generate_market_open_notifications()
        elif self._is_market_state_post():
            self._generate_market_closed_notifications()

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
        return any(n.type == notification_type for n in self._notifications) or any(
            n.type == notification_type for n in self._pending_notifications
        )

    def _is_close_to_sma(self, sma: Decimal | None) -> bool:
        if sma is None or self.previous_close_price is None:
            return False

        change_percentage = (sma - self.current_price) / self.current_price * 100

        return (
            self.previous_close_price < sma
            and self.current_price < sma
            and change_percentage <= self._CLOSE_TO_SMA_THRESHOLD
        ) or (
            self.previous_close_price > sma
            and self.current_price > sma
            and change_percentage >= -self._CLOSE_TO_SMA_THRESHOLD
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

        return _calculate_percentage_change(self.current_price, self.previous_close_price)

    def _is_market_state_open(self) -> bool:
        return self._market_state == MarketState.OPEN

    def _is_market_state_post(self) -> bool:
        return self._market_state == MarketState.POST

    def _is_crypto(self) -> bool:
        return self._kind == InstrumentType.CRYPTO

    def _generate_percentage_change_notification(
        self, change_percentage: Decimal
    ) -> Notification | None:
        if self._kind == InstrumentType.STOCK:
            inc = self._STOCK_INCREASE_THRESHOLDS
            dec = self._STOCK_DECREASE_THRESHOLDS
        elif self._kind == InstrumentType.CRYPTO:
            inc = self._CRYPTO_INCREASE_THRESHOLDS
            dec = self._CRYPTO_DECREASE_THRESHOLDS
        else:
            inc = self._DEFAULT_INCREASE_THRESHOLDS
            dec = self._DEFAULT_DECREASE_THRESHOLDS

        if change_percentage > 0:
            for threshold, notification_type in inc:
                if change_percentage >= threshold:
                    return Notification.create_percentage_change(
                        notification_type, self.symbol, self.current_price, change_percentage
                    )
        elif change_percentage < 0:
            for threshold, notification_type in dec:
                if change_percentage <= threshold:
                    return Notification.create_percentage_change(
                        notification_type, self.symbol, self.current_price, change_percentage
                    )

        return None

    def _generate_new_52_week_high_notification(self) -> None:
        if (
            self._snapshot is not None
            and self._snapshot.fifty_two_week_high is not None
            and self.current_price > self._snapshot.fifty_two_week_high
            and not self._has_notification_type(NotificationType.NEW_52_WEEK_HIGH)
        ):
            change_pct = self._change_percentage_from_previous_close()
            if change_pct is None:
                return
            self._pending_notifications.append(
                Notification.create_new_52_week_high(self.symbol, self.current_price, change_pct)
            )

    def _generate_new_52_week_low_notification(self) -> None:
        if (
            self._snapshot is not None
            and self._snapshot.fifty_two_week_low is not None
            and self.current_price < self._snapshot.fifty_two_week_low
            and not self._has_notification_type(NotificationType.NEW_52_WEEK_LOW)
        ):
            change_pct = self._change_percentage_from_previous_close()
            if change_pct is None:
                return
            self._pending_notifications.append(
                Notification.create_new_52_week_low(self.symbol, self.current_price, change_pct)
            )

    def _generate_regular_market_open_notification(self) -> None:
        if self._is_crypto() or self._has_notification_type(NotificationType.REGULAR_MARKET_OPEN):
            return
        self._pending_notifications.append(
            Notification.create_regular_market_open(
                self.symbol,
                self.open_price if self.open_price is not None else self.current_price,
                self.previous_close_price,
            )
        )

    def _generate_close_to_fifty_day_average_notification(self) -> None:
        if (
            self._is_close_to_sma(self.fifty_day_average)
            and not self._has_notification_type(NotificationType.CLOSE_TO_SMA50)
            and not self._has_notification_type(NotificationType.SMA50_CROSSED)
        ):
            change_pct = self._change_percentage_from_previous_close()
            if change_pct is None:
                return
            self._pending_notifications.append(
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
            self._pending_notifications.append(
                Notification.create_fifty_day_average_crossed(
                    self.symbol, self.current_price, change_pct, self.fifty_day_average
                )
            )

    def _generate_close_to_two_hundred_day_average_notification(self) -> None:
        if (
            self._is_close_to_sma(self.two_hundred_day_average)
            and not self._has_notification_type(NotificationType.CLOSE_TO_SMA200)
            and not self._has_notification_type(NotificationType.SMA200_CROSSED)
        ):
            change_pct = self._change_percentage_from_previous_close()
            if change_pct is None:
                return
            self._pending_notifications.append(
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
            self._pending_notifications.append(
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
            if self._has_pending_sma_notification() or self._has_pending_52_week_notification():
                self._notifications.append(notification)
            else:
                self._pending_notifications.append(notification)

    def _has_any_increase_percentage_notification(self) -> bool:
        increase_types = {
            NotificationType.LEVEL_1_INCREASE,
            NotificationType.LEVEL_2_INCREASE,
            NotificationType.LEVEL_3_INCREASE,
            NotificationType.LEVEL_4_INCREASE,
            NotificationType.LEVEL_5_INCREASE,
        }
        return any(n.type in increase_types for n in self._notifications)

    def _has_any_decrease_percentage_notification(self) -> bool:
        decrease_types = {
            NotificationType.LEVEL_1_DECREASE,
            NotificationType.LEVEL_2_DECREASE,
            NotificationType.LEVEL_3_DECREASE,
            NotificationType.LEVEL_4_DECREASE,
            NotificationType.LEVEL_5_DECREASE,
        }
        return any(n.type in decrease_types for n in self._notifications)

    def _generate_session_gains_erased_notification(self) -> None:
        change_percentage = self._change_percentage_from_previous_close()
        if (
            change_percentage is not None
            and change_percentage < 0
            and self._has_any_increase_percentage_notification()
            and not self._has_notification_type(NotificationType.SESSION_GAINS_ERASED)
        ):
            self._pending_notifications.append(
                Notification.create_session_gains_erased(
                    self.symbol, self.current_price, change_percentage
                )
            )
            self._reset_increase_percentage_notifications()

    def _generate_session_losses_erased_notification(self) -> None:
        change_percentage = self._change_percentage_from_previous_close()
        if (
            change_percentage is not None
            and change_percentage > 0
            and self._has_any_decrease_percentage_notification()
            and not self._has_notification_type(NotificationType.SESSION_LOSSES_ERASED)
        ):
            self._pending_notifications.append(
                Notification.create_session_losses_erased(
                    self.symbol, self.current_price, change_percentage
                )
            )
            self._reset_decrease_percentage_notifications()

    def _has_pending_sma_notification(self) -> bool:
        sma_types = {
            NotificationType.SMA50_CROSSED,
            NotificationType.SMA200_CROSSED,
            NotificationType.CLOSE_TO_SMA50,
            NotificationType.CLOSE_TO_SMA200,
        }
        return any(n.type in sma_types for n in self._pending_notifications)

    def _has_pending_52_week_notification(self) -> bool:
        week_types = {
            NotificationType.NEW_52_WEEK_HIGH,
            NotificationType.NEW_52_WEEK_LOW,
        }
        return any(n.type in week_types for n in self._pending_notifications)

    def _generate_target_price_notifications(self) -> None:
        remaining: list[TargetPrice] = []
        for target in self._targets:
            if target.is_reached(self):
                self._pending_notifications.append(
                    Notification.create_target_price_reached(self._symbol, target.target)
                )
                self._fulfilled_targets.append(target)
            else:
                remaining.append(target)
        self._targets = remaining

    def _generate_market_open_notifications(self) -> None:
        had_market_open = self._has_notification_type(NotificationType.REGULAR_MARKET_OPEN)
        self._generate_regular_market_open_notification()
        if not had_market_open and not self._is_crypto():
            return
        self._generate_fifty_day_average_crossed_notification()
        self._generate_close_to_fifty_day_average_notification()
        self._generate_two_hundred_day_average_crossed_notification()
        self._generate_close_to_two_hundred_day_average_notification()
        self._generate_new_52_week_high_notification()
        self._generate_new_52_week_low_notification()
        self._generate_percentage_change_from_previous_close_notification()
        self._generate_session_gains_erased_notification()
        self._generate_session_losses_erased_notification()
        self._generate_target_price_notifications()

    def _generate_regular_market_closed_notification(self) -> None:
        if self._has_notification_type(NotificationType.REGULAR_MARKET_CLOSED):
            return
        self._pending_notifications.append(
            Notification.create_regular_market_closed(
                self.symbol, self.current_price, self.previous_close_price
            )
        )

    def _reset_increase_percentage_notifications(self) -> None:
        increase_types = {
            NotificationType.LEVEL_1_INCREASE,
            NotificationType.LEVEL_2_INCREASE,
            NotificationType.LEVEL_3_INCREASE,
            NotificationType.LEVEL_4_INCREASE,
            NotificationType.LEVEL_5_INCREASE,
        }
        self._notifications = [n for n in self._notifications if n.type not in increase_types]

    def _reset_decrease_percentage_notifications(self) -> None:
        decrease_types = {
            NotificationType.LEVEL_1_DECREASE,
            NotificationType.LEVEL_2_DECREASE,
            NotificationType.LEVEL_3_DECREASE,
            NotificationType.LEVEL_4_DECREASE,
            NotificationType.LEVEL_5_DECREASE,
        }
        self._notifications = [n for n in self._notifications if n.type not in decrease_types]

    def _generate_market_closed_notifications(self) -> None:
        if self._is_crypto():
            return
        self._generate_regular_market_closed_notification()

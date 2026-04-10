from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from pryces.domain.stocks import Currency
from pryces.domain.utils import calculate_percentage_change


class StatisticsPeriod(str, Enum):
    ONE_DAY = "1D"
    ONE_WEEK = "1W"
    THREE_MONTHS = "3M"
    ONE_YEAR = "1Y"
    YEAR_TO_DATE = "YTD"


@dataclass(frozen=True, slots=True)
class HistoricalClose:
    period: StatisticsPeriod
    close_price: Decimal


class PriceChange:
    __slots__ = ("_period", "_close_price", "_change", "_change_percentage")

    def __init__(
        self,
        *,
        period: StatisticsPeriod,
        close_price: Decimal,
        current_price: Decimal,
    ) -> None:
        self._period = period
        self._close_price = close_price
        self._change = current_price - close_price
        self._change_percentage = calculate_percentage_change(current_price, close_price)

    @property
    def period(self) -> StatisticsPeriod:
        return self._period

    @property
    def close_price(self) -> Decimal:
        return self._close_price

    @property
    def change(self) -> Decimal:
        return self._change

    @property
    def change_percentage(self) -> Decimal:
        return self._change_percentage


class StockStatistics:
    __slots__ = ("_symbol", "_name", "_currency", "_current_price", "_price_changes")

    def __init__(
        self,
        *,
        symbol: str,
        current_price: Decimal,
        historical_closes: list[HistoricalClose],
        name: str | None = None,
        currency: Currency | None = None,
    ) -> None:
        self._symbol = symbol
        self._current_price = current_price
        self._name = name
        self._currency = currency
        self._price_changes: list[PriceChange] = [
            PriceChange(
                period=hc.period,
                close_price=hc.close_price,
                current_price=current_price,
            )
            for hc in historical_closes
        ]

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def currency(self) -> Currency | None:
        return self._currency

    @property
    def current_price(self) -> Decimal:
        return self._current_price

    @property
    def price_changes(self) -> list[PriceChange]:
        return list(self._price_changes)

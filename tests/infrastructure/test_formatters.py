from decimal import Decimal

import pytest

from pryces.domain.notifications import (
    Notification,
    NotificationFormatter,
    NotificationType,
    StockContext,
)
from pryces.domain.stock_statistics import HistoricalClose, StatisticsPeriod, StockStatistics
from pryces.infrastructure.formatters import (
    ConsolidatingNotificationFormatter,
    RegularStockStatisticsFormatter,
)
from pryces.domain.stocks import Currency


def _make_stats(
    current_price: str = "182.50",
    historical_closes: list[HistoricalClose] | None = None,
) -> StockStatistics:
    if historical_closes is None:
        historical_closes = [
            HistoricalClose(StatisticsPeriod.ONE_DAY, Decimal("181.20")),
            HistoricalClose(StatisticsPeriod.ONE_WEEK, Decimal("179.00")),
        ]
    return StockStatistics(
        symbol="AAPL",
        current_price=Decimal(current_price),
        historical_closes=historical_closes,
    )


class TestConsolidatingNotificationFormatter:

    def setup_method(self):
        self.formatter = ConsolidatingNotificationFormatter()
        self.context = StockContext(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("148.50"),
        )

    def test_milestones_consolidated_under_header_only_notification(self):
        header = Notification.create_percentage_change(
            NotificationType.LEVEL_1_INCREASE, "AAPL", Decimal("150.00"), Decimal("1.01")
        )
        milestone = Notification.create_fifty_day_average_crossed(Decimal("145.00"))

        result = self.formatter.format([header, milestone], self.context)

        assert len(result) == 1
        assert header.message in result[0]
        assert milestone.message in result[0]

    def test_multiple_milestones_consolidated_into_single_message(self):
        header = Notification.create_percentage_change(
            NotificationType.LEVEL_1_INCREASE, "AAPL", Decimal("150.00"), Decimal("1.01")
        )
        sma50 = Notification.create_fifty_day_average_crossed(Decimal("145.00"))
        high = Notification.create_new_52_week_high()

        result = self.formatter.format([header, sma50, high], self.context)

        assert len(result) == 1
        assert sma50.message in result[0]
        assert high.message in result[0]

    def test_header_only_emitted_individually_when_no_milestones(self):
        header = Notification.create_percentage_change(
            NotificationType.LEVEL_1_INCREASE, "AAPL", Decimal("150.00"), Decimal("1.01")
        )

        result = self.formatter.format([header], self.context)

        assert result == [header.message]

    def test_market_open_emitted_individually_when_no_milestones(self):
        market_open = Notification.create_regular_market_open(
            "AAPL", Decimal("150.00"), Decimal("148.50")
        )

        result = self.formatter.format([market_open], self.context)

        assert result == [market_open.message]

    def test_market_open_as_header_when_milestones_present(self):
        market_open = Notification.create_regular_market_open(
            "AAPL", Decimal("150.00"), Decimal("148.50")
        )
        milestone = Notification.create_fifty_day_average_crossed(Decimal("145.00"))

        result = self.formatter.format([market_open, milestone], self.context)

        assert len(result) == 1
        assert market_open.message in result[0]
        assert milestone.message in result[0]

    def test_market_open_takes_header_priority_over_percentage(self):
        market_open = Notification.create_regular_market_open(
            "AAPL", Decimal("150.00"), Decimal("148.50")
        )
        percentage = Notification.create_percentage_change(
            NotificationType.LEVEL_1_INCREASE, "AAPL", Decimal("150.00"), Decimal("1.01")
        )
        milestone = Notification.create_fifty_day_average_crossed(Decimal("145.00"))

        result = self.formatter.format([market_open, percentage, milestone], self.context)

        assert len(result) == 1
        lines = result[0].split("\n")
        assert market_open.message == lines[0]
        assert percentage.message in lines
        assert milestone.message in lines

    def test_market_open_as_header_with_percentage_when_no_milestones(self):
        market_open = Notification.create_regular_market_open(
            "AAPL", Decimal("150.00"), Decimal("148.50")
        )
        percentage = Notification.create_percentage_change(
            NotificationType.LEVEL_1_INCREASE, "AAPL", Decimal("150.00"), Decimal("1.01")
        )

        result = self.formatter.format([market_open, percentage], self.context)

        assert len(result) == 1
        lines = result[0].split("\n")
        assert market_open.message == lines[0]
        assert percentage.message == lines[1]

    def test_standalone_emitted_separately_from_consolidated_milestones(self):
        header = Notification.create_percentage_change(
            NotificationType.LEVEL_1_INCREASE, "AAPL", Decimal("150.00"), Decimal("1.01")
        )
        milestone = Notification.create_fifty_day_average_crossed(Decimal("145.00"))
        target = Notification.create_target_price_reached("AAPL", Decimal("150.00"))

        result = self.formatter.format([header, milestone, target], self.context)

        assert len(result) == 2
        assert milestone.message in result[0]
        assert result[1] == target.message

    def test_percentage_suppressed_when_milestones_exist(self):
        header = Notification.create_percentage_change(
            NotificationType.LEVEL_2_INCREASE, "AAPL", Decimal("150.00"), Decimal("3.75")
        )
        milestone = Notification.create_new_52_week_high()

        result = self.formatter.format([header, milestone], self.context)

        assert len(result) == 1
        assert header.message in result[0]
        assert milestone.message in result[0]

    def test_fallback_header_from_context_when_no_header_only(self):
        milestone = Notification.create_fifty_day_average_crossed(Decimal("145.00"))

        result = self.formatter.format([milestone], self.context)

        assert len(result) == 1
        assert "AAPL" in result[0]
        assert "150.00" in result[0]
        assert milestone.message in result[0]

    def test_fallback_header_plain_when_no_previous_close(self):
        context = StockContext(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=None,
        )
        milestone = Notification.create_fifty_day_average_crossed(Decimal("145.00"))

        result = self.formatter.format([milestone], context)

        assert len(result) == 1
        assert "AAPL at 150.00" in result[0]
        assert milestone.message in result[0]

    def test_empty_notifications_returns_empty(self):
        result = self.formatter.format([], self.context)

        assert result == []

    def test_header_found_anywhere_in_list_not_just_first(self):
        milestone = Notification.create_new_52_week_high()
        header = Notification.create_percentage_change(
            NotificationType.LEVEL_1_INCREASE, "AAPL", Decimal("150.00"), Decimal("1.01")
        )

        result = self.formatter.format([milestone, header], self.context)

        assert len(result) == 1
        assert header.message in result[0]
        assert milestone.message in result[0]


class TestRegularStockStatisticsFormatter:
    def setup_method(self):
        self.formatter = RegularStockStatisticsFormatter()

    def test_header_contains_symbol_and_current_price(self):
        result = self.formatter.format(_make_stats())

        assert result.startswith("📊 AAPL — 182.50")

    def test_positive_change_shows_plus_sign_and_up_icon(self):
        stats = _make_stats(
            current_price="182.50",
            historical_closes=[HistoricalClose(StatisticsPeriod.ONE_DAY, Decimal("181.20"))],
        )

        result = self.formatter.format(stats)

        assert "+" in result
        assert "📈" in result

    def test_negative_change_shows_no_plus_sign_and_down_icon(self):
        stats = _make_stats(
            current_price="175.00",
            historical_closes=[HistoricalClose(StatisticsPeriod.ONE_WEEK, Decimal("179.00"))],
        )

        result = self.formatter.format(stats)

        assert "📉" in result
        assert "+" not in result.split("\n")[1]

    def test_each_period_appears_on_its_own_line(self):
        result = self.formatter.format(_make_stats())
        lines = result.splitlines()

        periods = [line for line in lines if "1D" in line or "1W" in line]
        assert len(periods) == 2

    def test_empty_price_changes_shows_fallback_message(self):
        stats = _make_stats(historical_closes=[])

        result = self.formatter.format(stats)

        assert "No historical data available" in result

    def test_empty_price_changes_still_includes_header(self):
        stats = _make_stats(historical_closes=[])

        result = self.formatter.format(stats)

        assert result.startswith("📊 AAPL — 182.50")

    def test_zero_change_shows_equal_icon(self):
        stats = _make_stats(
            current_price="182.50",
            historical_closes=[HistoricalClose(StatisticsPeriod.ONE_DAY, Decimal("182.50"))],
        )

        result = self.formatter.format(stats)

        assert "🟰" in result
        assert "📈" not in result
        assert "📉" not in result

    def test_close_price_appears_in_output(self):
        result = self.formatter.format(_make_stats())

        assert "181.20" in result
        assert "179.00" in result

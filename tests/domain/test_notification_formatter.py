from decimal import Decimal

from pryces.domain.notification_formatter import ConsolidatingNotificationFormatter
from pryces.domain.notification_formatter import StockContext
from pryces.domain.notifications import Notification, NotificationType


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

    def test_standalone_notifications_emitted_separately(self):
        market_open = Notification.create_regular_market_open(
            "AAPL", Decimal("150.00"), Decimal("148.50")
        )

        result = self.formatter.format([market_open], self.context)

        assert result == [market_open.message]

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

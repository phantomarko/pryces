from pryces.domain.notifications import (
    MILESTONE_NOTIFICATION_TYPES,
    STANDALONE_NOTIFICATION_TYPES,
    Notification,
    NotificationFormatter,
    NotificationType,
    StockContext,
)
from pryces.domain.stock_statistics import StockStatistics, StockStatisticsFormatter
from pryces.domain.utils import calculate_percentage_change


class ConsolidatingNotificationFormatter(NotificationFormatter):
    def format(self, notifications: list[Notification], context: StockContext) -> list[str]:
        standalone: list[Notification] = []
        consolidatable: list[Notification] = []

        for n in notifications:
            if n.type in STANDALONE_NOTIFICATION_TYPES:
                standalone.append(n)
            else:
                consolidatable.append(n)

        messages: list[str] = []

        if consolidatable:
            header = self._pick_header(consolidatable, context)
            body = [n.message for n in consolidatable if n is not header]
            lines = [header.message] + body
            messages.append("\n".join(lines))

        for n in standalone:
            messages.append(n.message)

        return messages

    def _pick_header(
        self, consolidatable: list[Notification], context: StockContext
    ) -> Notification:
        for n in consolidatable:
            if n.type == NotificationType.REGULAR_MARKET_OPEN:
                return n
        for n in consolidatable:
            if (
                n.type != NotificationType.REGULAR_MARKET_OPEN
                and n.type not in MILESTONE_NOTIFICATION_TYPES
            ):
                return n
        return self._generate_fallback_header(context)

    def _generate_fallback_header(self, context: StockContext) -> Notification:
        if context.previous_close_price is None:
            return Notification.create_plain_header(context.symbol, context.current_price)
        change_pct = calculate_percentage_change(
            context.current_price, context.previous_close_price
        )
        return Notification.create_percentage_change(
            NotificationType.LEVEL_1_INCREASE,
            context.symbol,
            context.current_price,
            change_pct,
        )


class RegularStockStatisticsFormatter(StockStatisticsFormatter):
    def format(self, stats: StockStatistics) -> str:
        header = f"📊 {stats.symbol} — {stats.current_price:.2f}"
        lines = [header]
        if not stats.price_changes:
            lines.append("No historical data available")
            return "\n".join(lines)
        for pc in stats.price_changes:
            sign = "+" if pc.change_percentage > 0 else ""
            pct_str = f"{sign}{pc.change_percentage:.2f}%"
            icon = "📈" if pc.change_percentage >= 0 else "📉"
            lines.append(f"{icon} {pc.period.value:<3}  {pc.close_price:.2f}  {pct_str}")
        return "\n".join(lines)

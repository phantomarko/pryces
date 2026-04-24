from decimal import Decimal

from pryces.domain.stock_statistics import (
    HistoricalClose,
    PriceChange,
    RegularStockStatisticsFormatter,
    StatisticsPeriod,
    StockStatistics,
)
from pryces.domain.stocks import Currency


class TestPriceChange:
    def test_computes_positive_change(self):
        pc = PriceChange(
            period=StatisticsPeriod.ONE_DAY,
            close_price=Decimal("100"),
            current_price=Decimal("110"),
        )
        assert pc.change == Decimal("10")

    def test_computes_negative_change(self):
        pc = PriceChange(
            period=StatisticsPeriod.ONE_WEEK,
            close_price=Decimal("200"),
            current_price=Decimal("180"),
        )
        assert pc.change == Decimal("-20")

    def test_computes_percentage_change(self):
        pc = PriceChange(
            period=StatisticsPeriod.THREE_MONTHS,
            close_price=Decimal("100"),
            current_price=Decimal("125"),
        )
        assert pc.change_percentage == Decimal("25")

    def test_computes_negative_percentage_change(self):
        pc = PriceChange(
            period=StatisticsPeriod.ONE_YEAR,
            close_price=Decimal("200"),
            current_price=Decimal("150"),
        )
        assert pc.change_percentage == Decimal("-25")

    def test_exposes_period_and_close_price(self):
        pc = PriceChange(
            period=StatisticsPeriod.YEAR_TO_DATE,
            close_price=Decimal("95.50"),
            current_price=Decimal("100"),
        )
        assert pc.period == StatisticsPeriod.YEAR_TO_DATE
        assert pc.close_price == Decimal("95.50")


class TestStockStatistics:
    def test_construction_with_historical_closes(self):
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[
                HistoricalClose(StatisticsPeriod.ONE_DAY, Decimal("145")),
                HistoricalClose(StatisticsPeriod.ONE_YEAR, Decimal("120")),
            ],
        )
        assert stats.symbol == "AAPL"
        assert stats.current_price == Decimal("150")
        assert len(stats.price_changes) == 2

    def test_construction_with_empty_historical_closes(self):
        stats = StockStatistics(
            symbol="MSFT",
            current_price=Decimal("400"),
            historical_closes=[],
        )
        assert stats.price_changes == []

    def test_optional_name(self):
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[],
            name="Apple Inc.",
        )
        assert stats.name == "Apple Inc."

    def test_name_defaults_to_none(self):
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[],
        )
        assert stats.name is None

    def test_optional_currency(self):
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[],
            currency=Currency.USD,
        )
        assert stats.currency == Currency.USD

    def test_currency_defaults_to_none(self):
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[],
        )
        assert stats.currency is None

    def test_price_changes_are_precomputed(self):
        stats = StockStatistics(
            symbol="TSLA",
            current_price=Decimal("200"),
            historical_closes=[
                HistoricalClose(StatisticsPeriod.ONE_WEEK, Decimal("180")),
            ],
        )
        pc = stats.price_changes[0]
        assert pc.period == StatisticsPeriod.ONE_WEEK
        assert pc.close_price == Decimal("180")
        assert pc.change == Decimal("20")
        assert pc.change_percentage == (Decimal("200") - Decimal("180")) / Decimal("180") * 100

    def test_price_changes_returns_copy(self):
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[
                HistoricalClose(StatisticsPeriod.ONE_DAY, Decimal("145")),
            ],
        )
        changes = stats.price_changes
        changes.clear()
        assert len(stats.price_changes) == 1

    def test_format_delegates_to_formatter(self):
        formatter = RegularStockStatisticsFormatter()
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[],
        )

        result = stats.format(formatter)

        assert result.startswith("📊 AAPL — 150.00")

    def test_preserves_period_order(self):
        stats = StockStatistics(
            symbol="GOOG",
            current_price=Decimal("170"),
            historical_closes=[
                HistoricalClose(StatisticsPeriod.ONE_YEAR, Decimal("130")),
                HistoricalClose(StatisticsPeriod.ONE_DAY, Decimal("168")),
                HistoricalClose(StatisticsPeriod.THREE_MONTHS, Decimal("155")),
            ],
        )
        periods = [pc.period for pc in stats.price_changes]
        assert periods == [
            StatisticsPeriod.ONE_YEAR,
            StatisticsPeriod.ONE_DAY,
            StatisticsPeriod.THREE_MONTHS,
        ]


def _make_stats(
    symbol: str = "AAPL",
    current_price: str = "182.50",
    historical_closes: list[HistoricalClose] | None = None,
) -> StockStatistics:
    return StockStatistics(
        symbol=symbol,
        current_price=Decimal(current_price),
        historical_closes=(
            historical_closes
            if historical_closes is not None
            else [
                HistoricalClose(StatisticsPeriod.ONE_DAY, Decimal("181.20")),
                HistoricalClose(StatisticsPeriod.ONE_WEEK, Decimal("179.00")),
            ]
        ),
    )


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

    def test_close_price_appears_in_output(self):
        result = self.formatter.format(_make_stats())

        assert "181.20" in result
        assert "179.00" in result

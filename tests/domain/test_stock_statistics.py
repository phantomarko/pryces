from decimal import Decimal

from pryces.domain.stock_statistics import (
    HistoricalClose,
    PriceChange,
    StatisticsPeriod,
    StockStatistics,
)
from pryces.domain.stocks import Currency
from pryces.infrastructure.formatters import RegularStockStatisticsFormatter


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

from decimal import Decimal

from pryces.application.dtos import PriceChangeDTO, StockDTO, StockStatisticsDTO, TargetPriceDTO
from pryces.domain.stock_statistics import (
    HistoricalClose,
    PriceChange,
    StatisticsPeriod,
    StockStatistics,
)
from pryces.domain.stocks import Currency, Stock
from tests.fixtures.factories import create_stock


class TestStockDTO:

    def test_from_stock_returns_equivalent_dto(self):
        stock = create_stock("AAPL", Decimal("150.25"))

        result = StockDTO.from_stock(stock)

        assert isinstance(result, StockDTO)
        assert result.symbol == stock.symbol
        assert result.current_price == stock.current_price
        assert result.name == stock.name
        assert result.currency == "USD"
        assert result.previous_close_price == stock.previous_close_price
        assert result.open_price == stock.open_price
        assert result.day_high == stock.day_high
        assert result.day_low == stock.day_low
        assert result.fifty_day_average == stock.fifty_day_average
        assert result.two_hundred_day_average == stock.two_hundred_day_average
        assert result.fifty_two_week_high == stock.fifty_two_week_high
        assert result.fifty_two_week_low == stock.fifty_two_week_low
        assert result.market_cap == stock.market_cap
        assert result.price_delay_in_minutes == stock.price_delay_in_minutes

    def test_from_stock_with_minimal_fields(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.25"))

        result = StockDTO.from_stock(stock)

        assert isinstance(result, StockDTO)
        assert result.symbol == "AAPL"
        assert result.current_price == Decimal("150.25")
        assert result.name is None
        assert result.currency is None
        assert result.price_delay_in_minutes is None

    def test_from_stock_maps_price_delay_in_minutes(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.25"), price_delay_in_minutes=15)

        result = StockDTO.from_stock(stock)

        assert result.price_delay_in_minutes == 15


class TestTargetPriceDTO:

    def test_stores_symbol_and_target(self):
        dto = TargetPriceDTO(symbol="AAPL", target=Decimal("200.00"))

        assert dto.symbol == "AAPL"
        assert dto.target == Decimal("200.00")

    def test_is_immutable(self):
        dto = TargetPriceDTO(symbol="AAPL", target=Decimal("200.00"))

        import pytest

        with pytest.raises(Exception):
            dto.symbol = "TSLA"  # type: ignore[misc]

    def test_equality_with_same_values(self):
        dto_a = TargetPriceDTO(symbol="AAPL", target=Decimal("200.00"))
        dto_b = TargetPriceDTO(symbol="AAPL", target=Decimal("200.00"))

        assert dto_a == dto_b

    def test_inequality_with_different_symbol(self):
        dto_a = TargetPriceDTO(symbol="AAPL", target=Decimal("200.00"))
        dto_b = TargetPriceDTO(symbol="TSLA", target=Decimal("200.00"))

        assert dto_a != dto_b

    def test_inequality_with_different_target(self):
        dto_a = TargetPriceDTO(symbol="AAPL", target=Decimal("200.00"))
        dto_b = TargetPriceDTO(symbol="AAPL", target=Decimal("300.00"))

        assert dto_a != dto_b


class TestPriceChangeDTO:

    def test_from_price_change_maps_all_fields(self):
        pc = PriceChange(
            period=StatisticsPeriod.ONE_DAY,
            close_price=Decimal("100"),
            current_price=Decimal("110"),
        )

        result = PriceChangeDTO.from_price_change(pc)

        assert result.period == "1D"
        assert result.close_price == Decimal("100")
        assert result.change == Decimal("10")
        assert result.change_percentage == pc.change_percentage

    def test_from_price_change_maps_period_value(self):
        for period in StatisticsPeriod:
            pc = PriceChange(
                period=period,
                close_price=Decimal("100"),
                current_price=Decimal("105"),
            )
            dto = PriceChangeDTO.from_price_change(pc)
            assert dto.period == period.value


class TestStockStatisticsDTO:

    def test_from_stock_statistics_maps_basic_fields(self):
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[],
            name="Apple Inc.",
        )

        result = StockStatisticsDTO.from_stock_statistics(stats)

        assert result.symbol == "AAPL"
        assert result.current_price == Decimal("150")
        assert result.name == "Apple Inc."
        assert result.price_changes == []

    def test_from_stock_statistics_maps_currency_to_string(self):
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[],
            currency=Currency.EUR,
        )

        result = StockStatisticsDTO.from_stock_statistics(stats)

        assert result.currency == "EUR"

    def test_from_stock_statistics_maps_none_currency(self):
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[],
        )

        result = StockStatisticsDTO.from_stock_statistics(stats)

        assert result.currency is None

    def test_from_stock_statistics_maps_price_changes(self):
        stats = StockStatistics(
            symbol="AAPL",
            current_price=Decimal("150"),
            historical_closes=[
                HistoricalClose(StatisticsPeriod.ONE_WEEK, Decimal("130")),
                HistoricalClose(StatisticsPeriod.THREE_MONTHS, Decimal("120")),
            ],
        )

        result = StockStatisticsDTO.from_stock_statistics(stats)

        assert len(result.price_changes) == 2
        assert isinstance(result.price_changes[0], PriceChangeDTO)
        assert result.price_changes[0].period == "1W"
        assert result.price_changes[1].period == "3M"

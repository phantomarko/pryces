from decimal import Decimal

from pryces.application.dtos import StockDTO
from pryces.domain.stocks import Stock
from tests.fixtures.factories import create_stock


class TestStockDTO:

    def test_from_stock_returns_equivalent_dto(self):
        stock = create_stock("AAPL", Decimal("150.25"))

        result = StockDTO.from_stock(stock)

        assert isinstance(result, StockDTO)
        assert result.symbol == stock.symbol
        assert result.current_price == stock.current_price
        assert result.name == stock.name
        assert result.currency == stock.currency
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

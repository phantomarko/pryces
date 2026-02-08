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
        assert result.currentPrice == stock.currentPrice
        assert result.name == stock.name
        assert result.currency == stock.currency
        assert result.previousClosePrice == stock.previousClosePrice
        assert result.openPrice == stock.openPrice
        assert result.dayHigh == stock.dayHigh
        assert result.dayLow == stock.dayLow
        assert result.fiftyDayAverage == stock.fiftyDayAverage
        assert result.twoHundredDayAverage == stock.twoHundredDayAverage
        assert result.fiftyTwoWeekHigh == stock.fiftyTwoWeekHigh
        assert result.fiftyTwoWeekLow == stock.fiftyTwoWeekLow
        assert result.notifications == []

    def test_from_stock_with_minimal_fields(self):
        stock = Stock(symbol="AAPL", currentPrice=Decimal("150.25"))

        result = StockDTO.from_stock(stock)

        assert isinstance(result, StockDTO)
        assert result.symbol == "AAPL"
        assert result.currentPrice == Decimal("150.25")
        assert result.name is None
        assert result.currency is None
        assert result.notifications == []

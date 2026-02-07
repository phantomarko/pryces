from decimal import Decimal

from pryces.application.dtos import StockPriceDTO
from pryces.domain.stocks import Stock
from tests.fixtures.factories import create_stock


class TestStockPriceDTO:
    def test_to_stock_returns_equivalent_stock(self):
        dto = StockPriceDTO(
            symbol="AAPL",
            currentPrice=Decimal("150.25"),
            name="Apple Inc.",
            currency="USD",
            previousClosePrice=Decimal("148.50"),
            openPrice=Decimal("149.00"),
            dayHigh=Decimal("151.00"),
            dayLow=Decimal("148.00"),
            fiftyDayAverage=Decimal("145.50"),
            twoHundredDayAverage=Decimal("140.00"),
            fiftyTwoWeekHigh=Decimal("180.00"),
            fiftyTwoWeekLow=Decimal("120.00"),
        )

        result = dto.to_stock()

        assert isinstance(result, Stock)
        assert result.symbol == "AAPL"
        assert result.currentPrice == Decimal("150.25")
        assert result.name == "Apple Inc."
        assert result.currency == "USD"
        assert result.previousClosePrice == Decimal("148.50")
        assert result.openPrice == Decimal("149.00")
        assert result.dayHigh == Decimal("151.00")
        assert result.dayLow == Decimal("148.00")
        assert result.fiftyDayAverage == Decimal("145.50")
        assert result.twoHundredDayAverage == Decimal("140.00")
        assert result.fiftyTwoWeekHigh == Decimal("180.00")
        assert result.fiftyTwoWeekLow == Decimal("120.00")

    def test_to_stock_with_minimal_fields(self):
        dto = StockPriceDTO(symbol="AAPL", currentPrice=Decimal("150.25"))

        result = dto.to_stock()

        assert isinstance(result, Stock)
        assert result.symbol == "AAPL"
        assert result.currentPrice == Decimal("150.25")
        assert result.name is None
        assert result.currency is None

    def test_from_stock_returns_equivalent_dto(self):
        stock = create_stock("AAPL", Decimal("150.25"))

        result = StockPriceDTO.from_stock(stock)

        assert isinstance(result, StockPriceDTO)
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

    def test_from_stock_with_minimal_fields(self):
        stock = Stock(symbol="AAPL", currentPrice=Decimal("150.25"))

        result = StockPriceDTO.from_stock(stock)

        assert isinstance(result, StockPriceDTO)
        assert result.symbol == "AAPL"
        assert result.currentPrice == Decimal("150.25")
        assert result.name is None
        assert result.currency is None

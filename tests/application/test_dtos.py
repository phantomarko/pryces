from decimal import Decimal

from pryces.application.dtos import StockPriceDTO
from pryces.application.interfaces import StockPrice
from tests.fixtures.factories import create_stock_price


class TestStockPriceDTO:
    def test_to_stock_price_returns_equivalent_stock_price(self):
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

        result = dto.to_stock_price()

        assert isinstance(result, StockPrice)
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

    def test_to_stock_price_with_minimal_fields(self):
        dto = StockPriceDTO(symbol="AAPL", currentPrice=Decimal("150.25"))

        result = dto.to_stock_price()

        assert isinstance(result, StockPrice)
        assert result.symbol == "AAPL"
        assert result.currentPrice == Decimal("150.25")
        assert result.name is None
        assert result.currency is None

    def test_from_stock_price_returns_equivalent_dto(self):
        stock_price = create_stock_price("AAPL", Decimal("150.25"))

        result = StockPriceDTO.from_stock_price(stock_price)

        assert isinstance(result, StockPriceDTO)
        assert result.symbol == stock_price.symbol
        assert result.currentPrice == stock_price.currentPrice
        assert result.name == stock_price.name
        assert result.currency == stock_price.currency
        assert result.previousClosePrice == stock_price.previousClosePrice
        assert result.openPrice == stock_price.openPrice
        assert result.dayHigh == stock_price.dayHigh
        assert result.dayLow == stock_price.dayLow
        assert result.fiftyDayAverage == stock_price.fiftyDayAverage
        assert result.twoHundredDayAverage == stock_price.twoHundredDayAverage
        assert result.fiftyTwoWeekHigh == stock_price.fiftyTwoWeekHigh
        assert result.fiftyTwoWeekLow == stock_price.fiftyTwoWeekLow

    def test_from_stock_price_with_minimal_fields(self):
        stock_price = StockPrice(symbol="AAPL", currentPrice=Decimal("150.25"))

        result = StockPriceDTO.from_stock_price(stock_price)

        assert isinstance(result, StockPriceDTO)
        assert result.symbol == "AAPL"
        assert result.currentPrice == Decimal("150.25")
        assert result.name is None
        assert result.currency is None

from decimal import Decimal

from pryces.application.dtos import NotificationDTO, StockDTO
from pryces.domain.notifications import Notification, NotificationType
from pryces.domain.stocks import MarketState, Stock
from tests.fixtures.factories import create_stock


class TestNotificationDTO:

    def test_from_notification_maps_type_and_message(self):
        notification = Notification.create_fifty_day_average_crossed(
            "AAPL", Decimal("101"), Decimal("100")
        )

        result = NotificationDTO.from_notification(notification)

        assert isinstance(result, NotificationDTO)
        assert result.type == "SMA50_CROSSED"
        assert "AAPL" in result.message
        assert "50-day" in result.message

    def test_from_notification_maps_two_hundred_day_type(self):
        notification = Notification.create_two_hundred_day_average_crossed(
            "GOOGL", Decimal("201"), Decimal("200")
        )

        result = NotificationDTO.from_notification(notification)

        assert result.type == "SMA200_CROSSED"
        assert "GOOGL" in result.message
        assert "200-day" in result.message


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

    def test_from_stock_maps_notifications_to_notification_dtos(self):
        stock = Stock(
            symbol="AAPL",
            currentPrice=Decimal("101"),
            previousClosePrice=Decimal("99"),
            fiftyDayAverage=Decimal("100"),
            marketState=MarketState.OPEN,
        )
        stock.generate_milestones_notifications()

        result = StockDTO.from_stock(stock)

        assert len(result.notifications) == 2
        notification_types = {n.type for n in result.notifications}
        assert "REGULAR_MARKET_OPEN" in notification_types
        assert "SMA50_CROSSED" in notification_types
        sma_notification = next(n for n in result.notifications if n.type == "SMA50_CROSSED")
        assert isinstance(sma_notification, NotificationDTO)
        assert "50-day" in sma_notification.message

from decimal import Decimal
from unittest.mock import Mock

from pryces.application.dtos import TargetPriceDTO
from pryces.application.interfaces import MessageSender, StockProvider
from pryces.application.services import DelayWindowChecker, NotificationService, StockSynchronizer
from pryces.domain.stocks import MarketState, Stock
from pryces.infrastructure.repositories import InMemoryStockRepository
from pryces.application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
)
from tests.fixtures.factories import (
    create_stock_crossing_both_averages,
    create_stock_crossing_fifty_day,
    create_stock_crossing_two_hundred_day,
    create_stock_no_crossing,
)


class TestTriggerStocksNotifications:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockProvider)
        self.mock_sender = Mock(spec=MessageSender)
        self.mock_checker = Mock(spec=DelayWindowChecker)
        self.mock_checker.is_in_delay_window.return_value = False
        self.notification_service = NotificationService(self.mock_sender, self.mock_checker)
        self.stock_repository = InMemoryStockRepository()
        self.stock_synchronizer = StockSynchronizer(
            provider=self.mock_provider,
            stock_repository=self.stock_repository,
        )
        self.use_case = TriggerStocksNotifications(
            stock_synchronizer=self.stock_synchronizer,
            notification_service=self.notification_service,
        )

    def test_handle_sends_milestone_notification_for_fifty_day_crossing(self):
        stock = create_stock_crossing_fifty_day("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 2

    def test_handle_sends_milestone_notification_for_two_hundred_day_crossing(self):
        stock = create_stock_crossing_two_hundred_day("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["GOOGL"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 3

    def test_handle_sends_both_notifications_when_both_averages_crossed(self):
        stock = create_stock_crossing_both_averages("MSFT")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["MSFT"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 3

    def test_handle_sends_market_open_even_when_no_crossings(self):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        self.use_case.handle(request)

        self.mock_sender.send_message.assert_called_once()

    def test_handle_sends_notifications_for_all_stocks_with_market_open(self):
        crossing_stock = create_stock_crossing_fifty_day("AAPL")
        non_crossing_stock = create_stock_no_crossing("GOOGL")
        self.mock_provider.get_stocks.return_value = [crossing_stock, non_crossing_stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL", "GOOGL"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 3

    def test_handle_sends_notifications_for_multiple_stocks_with_crossings(self):
        stock1 = create_stock_crossing_fifty_day("AAPL")
        stock2 = create_stock_crossing_two_hundred_day("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock1, stock2]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL", "GOOGL"])

        self.use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 5

    def test_handle_does_nothing_for_empty_symbols(self):
        self.mock_provider.get_stocks.return_value = []
        request = TriggerStocksNotificationsRequest(symbols=[])

        self.use_case.handle(request)

        self.mock_sender.send_message.assert_not_called()
        self.mock_provider.get_stocks.assert_called_once_with([])

    def test_handle_calls_provider_with_correct_symbols(self):
        self.mock_provider.get_stocks.return_value = []
        request = TriggerStocksNotificationsRequest(symbols=["AAPL", "GOOGL", "MSFT"])

        self.use_case.handle(request)

        self.mock_provider.get_stocks.assert_called_once_with(["AAPL", "GOOGL", "MSFT"])

    def test_handle_sends_new_52_week_high_notification_when_past_stock_exists(self):
        past_stock = Stock(
            symbol="AAPL", current_price=Decimal("180.00"), fifty_two_week_high=Decimal("190.00")
        )
        self.stock_repository.save_batch([past_stock])
        current_stock = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            open_price=Decimal("195.00"),
            previous_close_price=Decimal("190.00"),
            market_state=MarketState.OPEN,
        )
        self.mock_provider.get_stocks.return_value = [current_stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        self.use_case.handle(request)

        messages = [call[0][0] for call in self.mock_sender.send_message.call_args_list]
        assert any("52-week high" in m for m in messages)

    def test_handle_returns_empty_list_when_no_targets_fulfilled(self):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        result = self.use_case.handle(request)

        assert result == []

    def test_handle_returns_fulfilled_target_as_dto(self):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(
            symbols=["AAPL"],
            targets={"AAPL": [stock.current_price]},
        )

        result = self.use_case.handle(request)

        assert result == [TargetPriceDTO(symbol="AAPL", target=stock.current_price)]

    def test_handle_returns_fulfilled_targets_from_multiple_stocks(self):
        stock_aapl = create_stock_no_crossing("AAPL")
        stock_googl = create_stock_no_crossing("GOOGL")
        self.mock_provider.get_stocks.return_value = [stock_aapl, stock_googl]
        request = TriggerStocksNotificationsRequest(
            symbols=["AAPL", "GOOGL"],
            targets={
                "AAPL": [stock_aapl.current_price],
                "GOOGL": [stock_googl.current_price],
            },
        )

        result = self.use_case.handle(request)

        assert len(result) == 2
        assert TargetPriceDTO(symbol="AAPL", target=stock_aapl.current_price) in result
        assert TargetPriceDTO(symbol="GOOGL", target=stock_googl.current_price) in result

    def test_handle_sends_new_52_week_low_notification_when_past_stock_exists(self):
        past_stock = Stock(
            symbol="AAPL", current_price=Decimal("120.00"), fifty_two_week_low=Decimal("110.00")
        )
        self.stock_repository.save_batch([past_stock])
        current_stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            open_price=Decimal("105.00"),
            previous_close_price=Decimal("110.00"),
            market_state=MarketState.OPEN,
        )
        self.mock_provider.get_stocks.return_value = [current_stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        self.use_case.handle(request)

        messages = [call[0][0] for call in self.mock_sender.send_message.call_args_list]
        assert any("52-week low" in m for m in messages)

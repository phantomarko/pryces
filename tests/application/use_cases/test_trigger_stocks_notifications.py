from decimal import Decimal
from unittest.mock import Mock

from pryces.application.dtos import TargetPriceDTO
from pryces.application.providers import StockProvider
from pryces.application.senders import MessageSender
from pryces.application.services import NotificationService
from pryces.domain.notifications import NotificationType
from pryces.domain.stocks import MarketState, Stock
from pryces.domain.target_prices import TargetPrice
from pryces.infrastructure.repositories import (
    InMemoryMarketTransitionRepository,
    InMemoryNotificationRepository,
    InMemoryStockRepository,
    InMemoryTargetPriceRepository,
)
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
        self.notification_service = NotificationService(
            self.mock_sender,
            InMemoryNotificationRepository(),
            InMemoryMarketTransitionRepository(),
        )
        self.target_price_repository = InMemoryTargetPriceRepository()
        self.use_case = TriggerStocksNotifications(
            provider=self.mock_provider,
            notification_service=self.notification_service,
            stock_repository=InMemoryStockRepository(),
            target_price_repository=self.target_price_repository,
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
        stock_repo = InMemoryStockRepository()
        stock_repo.save_batch([past_stock])
        self.use_case = TriggerStocksNotifications(
            provider=self.mock_provider,
            notification_service=self.notification_service,
            stock_repository=stock_repo,
            target_price_repository=self.target_price_repository,
        )
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

        # After handle(), past_stock has been updated via update() so check its notifications
        sent_types = {n.type for n in past_stock.notifications}
        assert NotificationType.NEW_52_WEEK_HIGH in sent_types

    def test_handle_sets_entry_price_on_targets_for_the_stock(self):
        target = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        self.target_price_repository.save(target)
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        self.use_case.handle(request)

        assert target.entry == stock.current_price

    def test_handle_does_not_overwrite_existing_entry_on_subsequent_calls(self):
        target = TargetPrice(symbol="AAPL", target=Decimal("200.00"))
        self.target_price_repository.save(target)
        first_stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [first_stock]
        self.use_case.handle(TriggerStocksNotificationsRequest(symbols=["AAPL"]))
        original_entry = target.entry

        second_stock = Stock(symbol="AAPL", current_price=Decimal("999.00"))
        self.mock_provider.get_stocks.return_value = [second_stock]
        self.use_case.handle(TriggerStocksNotificationsRequest(symbols=["AAPL"]))

        assert target.entry == original_entry

    def test_handle_returns_empty_list_when_no_targets_fulfilled(self):
        stock = create_stock_no_crossing("AAPL")
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        result = self.use_case.handle(request)

        assert result == []

    def test_handle_returns_fulfilled_target_as_dto(self):
        stock = create_stock_no_crossing("AAPL")
        target = TargetPrice(symbol="AAPL", target=stock.current_price)
        self.target_price_repository.save(target)
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        result = self.use_case.handle(request)

        assert result == [TargetPriceDTO(symbol="AAPL", target=stock.current_price)]

    def test_handle_removes_fulfilled_target_from_repository(self):
        stock = create_stock_no_crossing("AAPL")
        target = TargetPrice(symbol="AAPL", target=stock.current_price)
        self.target_price_repository.save(target)
        self.mock_provider.get_stocks.return_value = [stock]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL"])

        self.use_case.handle(request)

        assert self.target_price_repository.get_by_symbol(["AAPL"]) == []

    def test_handle_returns_fulfilled_targets_from_multiple_stocks(self):
        stock_aapl = create_stock_no_crossing("AAPL")
        stock_googl = create_stock_no_crossing("GOOGL")
        target_aapl = TargetPrice(symbol="AAPL", target=stock_aapl.current_price)
        target_googl = TargetPrice(symbol="GOOGL", target=stock_googl.current_price)
        self.target_price_repository.save(target_aapl)
        self.target_price_repository.save(target_googl)
        self.mock_provider.get_stocks.return_value = [stock_aapl, stock_googl]
        request = TriggerStocksNotificationsRequest(symbols=["AAPL", "GOOGL"])

        result = self.use_case.handle(request)

        assert len(result) == 2
        assert TargetPriceDTO(symbol="AAPL", target=stock_aapl.current_price) in result
        assert TargetPriceDTO(symbol="GOOGL", target=stock_googl.current_price) in result

    def test_handle_sends_new_52_week_low_notification_when_past_stock_exists(self):
        past_stock = Stock(
            symbol="AAPL", current_price=Decimal("120.00"), fifty_two_week_low=Decimal("110.00")
        )
        stock_repo = InMemoryStockRepository()
        stock_repo.save_batch([past_stock])
        self.use_case = TriggerStocksNotifications(
            provider=self.mock_provider,
            notification_service=self.notification_service,
            stock_repository=stock_repo,
            target_price_repository=self.target_price_repository,
        )
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

        # After handle(), past_stock has been updated via update() so check its notifications
        sent_types = {n.type for n in past_stock.notifications}
        assert NotificationType.NEW_52_WEEK_LOW in sent_types

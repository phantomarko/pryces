from decimal import Decimal
from unittest.mock import Mock, call

from pryces.application.interfaces import MessageSender, StockStatisticsProvider
from pryces.application.use_cases.trigger_stocks_statistics import (
    TriggerStocksStatistics,
    TriggerStocksStatisticsRequest,
)
from pryces.domain.stock_statistics import (
    StockStatistics,
    StockStatisticsFormatter,
)


def _make_stats(symbol: str = "AAPL", current_price: str = "150") -> StockStatistics:
    return StockStatistics(
        symbol=symbol, current_price=Decimal(current_price), historical_closes=[]
    )


def _make_use_case(provider, formatter=None, sender=None) -> TriggerStocksStatistics:
    if formatter is None:
        formatter = Mock(spec=StockStatisticsFormatter)
        formatter.format.return_value = "formatted"
    if sender is None:
        sender = Mock(spec=MessageSender)
    return TriggerStocksStatistics(provider=provider, formatter=formatter, sender=sender)


class TestTriggerStocksStatistics:

    def setup_method(self):
        self.mock_provider = Mock(spec=StockStatisticsProvider)
        self.mock_formatter = Mock(spec=StockStatisticsFormatter)
        self.mock_formatter.format.return_value = "formatted"
        self.mock_sender = Mock(spec=MessageSender)

    def test_handle_sends_nothing_for_empty_input(self):
        self.mock_provider.get_stock_statistics.return_value = []
        request = TriggerStocksStatisticsRequest(symbols=[])
        use_case = TriggerStocksStatistics(
            provider=self.mock_provider,
            formatter=self.mock_formatter,
            sender=self.mock_sender,
        )

        use_case.handle(request)

        self.mock_sender.send_message.assert_not_called()

    def test_handle_sends_one_message_per_stats(self):
        stats = [_make_stats("AAPL"), _make_stats("GOOGL")]
        self.mock_provider.get_stock_statistics.return_value = stats
        self.mock_formatter.format.side_effect = ["📊 AAPL", "📊 GOOGL"]
        request = TriggerStocksStatisticsRequest(symbols=["AAPL", "GOOGL"])
        use_case = TriggerStocksStatistics(
            provider=self.mock_provider,
            formatter=self.mock_formatter,
            sender=self.mock_sender,
        )

        use_case.handle(request)

        assert self.mock_sender.send_message.call_count == 2
        self.mock_sender.send_message.assert_has_calls([call("📊 AAPL"), call("📊 GOOGL")])

    def test_handle_passes_symbols_to_provider(self):
        self.mock_provider.get_stock_statistics.return_value = []
        request = TriggerStocksStatisticsRequest(symbols=["AAPL", "TSLA"])
        use_case = TriggerStocksStatistics(
            provider=self.mock_provider,
            formatter=self.mock_formatter,
            sender=self.mock_sender,
        )

        use_case.handle(request)

        self.mock_provider.get_stock_statistics.assert_called_once_with(["AAPL", "TSLA"])

    def test_handle_formats_each_stats_before_sending(self):
        stats = [_make_stats("AAPL"), _make_stats("TSLA")]
        self.mock_provider.get_stock_statistics.return_value = stats
        request = TriggerStocksStatisticsRequest(symbols=["AAPL", "TSLA"])
        use_case = TriggerStocksStatistics(
            provider=self.mock_provider,
            formatter=self.mock_formatter,
            sender=self.mock_sender,
        )

        use_case.handle(request)

        assert self.mock_formatter.format.call_count == 2
        self.mock_formatter.format.assert_any_call(stats[0])
        self.mock_formatter.format.assert_any_call(stats[1])

    def test_handle_returns_none(self):
        self.mock_provider.get_stock_statistics.return_value = []
        request = TriggerStocksStatisticsRequest(symbols=[])
        use_case = TriggerStocksStatistics(
            provider=self.mock_provider,
            formatter=self.mock_formatter,
            sender=self.mock_sender,
        )

        result = use_case.handle(request)

        assert result is None

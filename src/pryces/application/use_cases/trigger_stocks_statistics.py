from dataclasses import dataclass

from ...domain.stock_statistics import StockStatisticsFormatter
from ..interfaces import MessageSender, StockStatisticsProvider


@dataclass(frozen=True)
class TriggerStocksStatisticsRequest:
    symbols: list[str]


class TriggerStocksStatistics:
    def __init__(
        self,
        provider: StockStatisticsProvider,
        formatter: StockStatisticsFormatter,
        sender: MessageSender,
    ) -> None:
        self._provider = provider
        self._formatter = formatter
        self._sender = sender

    def handle(self, request: TriggerStocksStatisticsRequest) -> None:
        statistics = self._provider.get_stock_statistics(request.symbols)
        for stats in statistics:
            self._sender.send_message(stats.format(self._formatter))

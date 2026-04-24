from dataclasses import dataclass

from ...domain.stock_statistics import StockStatisticsFormatter
from ..interfaces import StockStatisticsProvider


@dataclass(frozen=True)
class GetStocksStatisticsRequest:
    symbols: list[str]


class GetStocksStatistics:
    def __init__(
        self, provider: StockStatisticsProvider, formatter: StockStatisticsFormatter
    ) -> None:
        self._provider = provider
        self._formatter = formatter

    def handle(self, request: GetStocksStatisticsRequest) -> list[str]:
        statistics = self._provider.get_stock_statistics(request.symbols)
        return [stats.format(self._formatter) for stats in statistics]

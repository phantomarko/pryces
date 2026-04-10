from dataclasses import dataclass

from ..dtos import StockStatisticsDTO
from ..interfaces import StockStatisticsProvider


@dataclass(frozen=True)
class GetStocksStatisticsRequest:
    symbols: list[str]


class GetStocksStatistics:
    def __init__(self, provider: StockStatisticsProvider) -> None:
        self._provider = provider

    def handle(self, request: GetStocksStatisticsRequest) -> list[StockStatisticsDTO]:
        statistics = self._provider.get_stock_statistics(request.symbols)
        return [StockStatisticsDTO.from_stock_statistics(stats) for stats in statistics]

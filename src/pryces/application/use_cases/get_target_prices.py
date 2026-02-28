from dataclasses import dataclass

from pryces.application.dtos import TargetPriceDTO
from pryces.application.repositories import TargetPriceRepository


@dataclass(frozen=True)
class GetTargetPricesRequest:
    symbols: list[str]


class GetTargetPrices:
    def __init__(self, repository: TargetPriceRepository) -> None:
        self._repository = repository

    def handle(self, request: GetTargetPricesRequest) -> list[TargetPriceDTO]:
        return [
            TargetPriceDTO.from_target_price(pt)
            for pt in self._repository.get_by_symbol(request.symbols)
        ]

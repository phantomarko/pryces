from dataclasses import dataclass

from pryces.application.dtos import TargetPriceDTO
from pryces.application.interfaces import TargetPriceRepository


@dataclass(frozen=True)
class SyncTargetPricesRequest:
    price_targets: list[TargetPriceDTO]


class SyncTargetPrices:
    def __init__(self, repository: TargetPriceRepository) -> None:
        self._repository = repository

    def handle(self, request: SyncTargetPricesRequest) -> None:
        symbols = list({dto.symbol for dto in request.price_targets})
        existing = self._repository.get_by_symbol(symbols)
        existing_keys = {(pt.symbol, pt.target) for pt in existing}
        requested_keys = {(dto.symbol, dto.target) for dto in request.price_targets}

        for dto in request.price_targets:
            if (dto.symbol, dto.target) not in existing_keys:
                self._repository.save(dto.to_target_price())

        for pt in existing:
            if (pt.symbol, pt.target) not in requested_keys:
                self._repository.delete(pt)

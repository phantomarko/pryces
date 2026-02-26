from dataclasses import dataclass

from pryces.application.dtos import TargetPriceDTO
from pryces.application.interfaces import TargetPriceRepository


@dataclass(frozen=True)
class UpdatePriceTargetsRequest:
    price_targets: list[TargetPriceDTO]


class UpdatePriceTargets:
    def __init__(self, repository: TargetPriceRepository) -> None:
        self._repository = repository

    def handle(self, request: UpdatePriceTargetsRequest) -> None:
        existing = {(pt.symbol, pt.target_price) for pt in self._repository.get_all()}

        for dto in request.price_targets:
            if (dto.symbol, dto.target) not in existing:
                self._repository.save(dto.to_target_price())

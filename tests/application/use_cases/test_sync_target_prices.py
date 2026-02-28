from decimal import Decimal

from pryces.application.dtos import TargetPriceDTO
from pryces.application.use_cases.sync_target_prices import (
    SyncTargetPrices,
    SyncTargetPricesRequest,
)
from pryces.infrastructure.repositories import InMemoryTargetPriceRepository


class TestSyncTargetPrices:

    def setup_method(self):
        self.repository = InMemoryTargetPriceRepository()
        self.use_case = SyncTargetPrices(self.repository)

    def test_new_targets_are_saved(self):
        request = SyncTargetPricesRequest(
            price_targets=[
                TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")),
                TargetPriceDTO(symbol="MSFT", target=Decimal("300.0")),
            ]
        )

        self.use_case.handle(request)

        saved = {(pt.symbol, pt.target) for pt in self.repository.get_by_symbol(["ASPI", "MSFT"])}
        assert saved == {("ASPI", Decimal("4.0")), ("MSFT", Decimal("300.0"))}

    def test_existing_target_with_same_symbol_and_price_is_skipped(self):
        existing = TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")).to_target_price()
        self.repository.save(existing)
        request = SyncTargetPricesRequest(
            price_targets=[TargetPriceDTO(symbol="ASPI", target=Decimal("4.0"))]
        )

        self.use_case.handle(request)

        saved = self.repository.get_by_symbol(["ASPI"])
        assert len(saved) == 1
        assert saved[0] is existing

    def test_same_symbol_different_price_replaces_old(self):
        self.repository.save(TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")).to_target_price())
        request = SyncTargetPricesRequest(
            price_targets=[TargetPriceDTO(symbol="ASPI", target=Decimal("5.1"))]
        )

        self.use_case.handle(request)

        saved = {(pt.symbol, pt.target) for pt in self.repository.get_by_symbol(["ASPI"])}
        assert saved == {("ASPI", Decimal("5.1"))}

    def test_targets_not_in_request_are_deleted(self):
        self.repository.save(TargetPriceDTO(symbol="ASPI", target=Decimal("1.4")).to_target_price())
        self.repository.save(TargetPriceDTO(symbol="ASPI", target=Decimal("3.2")).to_target_price())
        request = SyncTargetPricesRequest(
            price_targets=[
                TargetPriceDTO(symbol="ASPI", target=Decimal("3.2")),
                TargetPriceDTO(symbol="ASPI", target=Decimal("5.1")),
            ]
        )

        self.use_case.handle(request)

        saved = {(pt.symbol, pt.target) for pt in self.repository.get_by_symbol(["ASPI"])}
        assert saved == {("ASPI", Decimal("3.2")), ("ASPI", Decimal("5.1"))}

    def test_mixed_existing_and_new_saves_only_new(self):
        self.repository.save(TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")).to_target_price())
        request = SyncTargetPricesRequest(
            price_targets=[
                TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")),
                TargetPriceDTO(symbol="MSFT", target=Decimal("300.0")),
            ]
        )

        self.use_case.handle(request)

        saved = {(pt.symbol, pt.target) for pt in self.repository.get_by_symbol(["ASPI", "MSFT"])}
        assert saved == {("ASPI", Decimal("4.0")), ("MSFT", Decimal("300.0"))}

    def test_empty_request_saves_nothing(self):
        request = SyncTargetPricesRequest(price_targets=[])

        self.use_case.handle(request)

        assert self.repository.get_by_symbol([]) == []

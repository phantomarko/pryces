from decimal import Decimal

from pryces.application.dtos import TargetPriceDTO
from pryces.application.use_cases.get_target_prices import GetTargetPrices, GetTargetPricesRequest
from pryces.infrastructure.implementations import InMemoryTargetPriceRepository


class TestGetTargetPrices:

    def setup_method(self):
        self.repository = InMemoryTargetPriceRepository()
        self.use_case = GetTargetPrices(self.repository)

    def test_returns_empty_when_no_targets_exist_for_symbols(self):
        result = self.use_case.handle(GetTargetPricesRequest(symbols=["ASPI"]))

        assert result == []

    def test_returns_targets_for_requested_symbols(self):
        self.repository.save(TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")).to_target_price())
        self.repository.save(
            TargetPriceDTO(symbol="MSFT", target=Decimal("300.0")).to_target_price()
        )

        result = self.use_case.handle(GetTargetPricesRequest(symbols=["ASPI", "MSFT"]))

        assert set(result) == {
            TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")),
            TargetPriceDTO(symbol="MSFT", target=Decimal("300.0")),
        }

    def test_filters_out_targets_for_unrequested_symbols(self):
        self.repository.save(TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")).to_target_price())
        self.repository.save(
            TargetPriceDTO(symbol="MSFT", target=Decimal("300.0")).to_target_price()
        )

        result = self.use_case.handle(GetTargetPricesRequest(symbols=["ASPI"]))

        assert result == [TargetPriceDTO(symbol="ASPI", target=Decimal("4.0"))]

    def test_returns_multiple_targets_for_same_symbol(self):
        self.repository.save(TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")).to_target_price())
        self.repository.save(TargetPriceDTO(symbol="ASPI", target=Decimal("5.5")).to_target_price())

        result = self.use_case.handle(GetTargetPricesRequest(symbols=["ASPI"]))

        assert set(result) == {
            TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")),
            TargetPriceDTO(symbol="ASPI", target=Decimal("5.5")),
        }

    def test_returns_empty_when_symbols_list_is_empty(self):
        self.repository.save(TargetPriceDTO(symbol="ASPI", target=Decimal("4.0")).to_target_price())

        result = self.use_case.handle(GetTargetPricesRequest(symbols=[]))

        assert result == []

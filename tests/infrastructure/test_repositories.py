from datetime import datetime

import pytest

from pryces.infrastructure.repositories import (
    InMemoryMarketTransitionRepository,
    InMemoryStockRepository,
)
from tests.fixtures.factories import create_stock


class TestInMemoryStockRepository:
    def test_get_returns_none_when_symbol_not_saved(self):
        repo = InMemoryStockRepository()

        assert repo.get("AAPL") is None

    def test_save_batch_and_get_returns_saved_stock(self):
        repo = InMemoryStockRepository()
        stock = create_stock("AAPL")

        repo.save_batch([stock])

        assert repo.get("AAPL") is stock

    def test_save_batch_stores_multiple_stocks(self):
        repo = InMemoryStockRepository()
        aapl = create_stock("AAPL")
        msft = create_stock("MSFT")

        repo.save_batch([aapl, msft])

        assert repo.get("AAPL") is aapl
        assert repo.get("MSFT") is msft

    def test_save_batch_overwrites_existing_stock(self):
        repo = InMemoryStockRepository()
        original = create_stock("AAPL")
        updated = create_stock("AAPL")

        repo.save_batch([original])
        repo.save_batch([updated])

        assert repo.get("AAPL") is updated

    def test_get_returns_none_for_unknown_symbol_after_saves(self):
        repo = InMemoryStockRepository()
        repo.save_batch([create_stock("AAPL")])

        assert repo.get("MSFT") is None


class TestInMemoryMarketTransitionRepository:
    def test_get_returns_none_when_symbol_not_saved(self):
        repo = InMemoryMarketTransitionRepository()

        assert repo.get("AAPL") is None

    def test_save_and_get_returns_saved_transition_time(self):
        repo = InMemoryMarketTransitionRepository()
        transition_time = datetime(2024, 1, 15, 9, 30, 0)

        repo.save("AAPL", transition_time)

        assert repo.get("AAPL") == transition_time

    def test_save_overwrites_existing_transition_time(self):
        repo = InMemoryMarketTransitionRepository()
        first = datetime(2024, 1, 15, 9, 30, 0)
        second = datetime(2024, 1, 15, 14, 0, 0)

        repo.save("AAPL", first)
        repo.save("AAPL", second)

        assert repo.get("AAPL") == second

    def test_delete_removes_saved_symbol(self):
        repo = InMemoryMarketTransitionRepository()
        repo.save("AAPL", datetime(2024, 1, 15, 9, 30, 0))

        repo.delete("AAPL")

        assert repo.get("AAPL") is None

    def test_delete_non_existent_symbol_does_not_raise(self):
        repo = InMemoryMarketTransitionRepository()

        repo.delete("AAPL")  # should not raise

    def test_delete_only_removes_target_symbol(self):
        repo = InMemoryMarketTransitionRepository()
        aapl_time = datetime(2024, 1, 15, 9, 30, 0)
        msft_time = datetime(2024, 1, 15, 10, 0, 0)
        repo.save("AAPL", aapl_time)
        repo.save("MSFT", msft_time)

        repo.delete("AAPL")

        assert repo.get("AAPL") is None
        assert repo.get("MSFT") == msft_time

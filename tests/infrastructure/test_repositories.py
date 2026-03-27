from pryces.infrastructure.repositories import InMemoryStockRepository
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

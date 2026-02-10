class StockNotFound(Exception):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__(f"Stock not found: {symbol}")

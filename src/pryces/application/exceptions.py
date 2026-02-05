class StockNotFound(Exception):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__(f"Stock not found: {symbol}")


class StockInformationIncomplete(Exception):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__(
            f"Stock information incomplete: unable to retrieve current price for {symbol}"
        )

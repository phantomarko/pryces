class StockNotFound(Exception):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__(f"Stock not found: {symbol}")


class MessageSendingFailed(Exception):
    def __init__(self, reason: str, retryable: bool = False) -> None:
        self.retryable = retryable
        super().__init__(f"Message sending failed: {reason}")

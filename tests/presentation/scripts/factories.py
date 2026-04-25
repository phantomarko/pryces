from decimal import Decimal

from pryces.infrastructure.configs import MonitorStocksConfig, SymbolConfig


def make_symbol(symbol: str = "AAPL", prices: list = None) -> SymbolConfig:
    return SymbolConfig(symbol=symbol, prices=prices or [Decimal("5")])


def make_config(**overrides) -> MonitorStocksConfig:
    defaults = {
        "interval": 5,
        "symbols": [
            SymbolConfig("AAPL", [Decimal("150"), Decimal("200")]),
            SymbolConfig("GOOGL", [Decimal("100")]),
        ],
    }
    defaults.update(overrides)
    return MonitorStocksConfig(**defaults)

from __future__ import annotations

from ...application.dtos import TargetPriceDTO
from ...application.interfaces import LoggerFactory
from ...infrastructure.configs import ConfigManager, MonitorStocksConfig, SymbolConfig


class ConfigRefresher:
    def __init__(
        self,
        config_manager: ConfigManager,
        config: MonitorStocksConfig,
        logger_factory: LoggerFactory,
    ) -> None:
        self._config_manager = config_manager
        self._config = config
        self._logger = logger_factory.get_logger(__name__)

    @property
    def config(self) -> MonitorStocksConfig:
        return self._config

    def refresh(self) -> None:
        try:
            new_config = self._config_manager.read_monitor_stocks_config()
            if new_config != self._config:
                self._config = new_config
                self._logger.info("Config refreshed.")
                self.log_config()
        except Exception as e:
            self._logger.warning(f"Config refresh failed: {e}")

    def remove_fulfilled_targets(self, fulfilled: list[TargetPriceDTO]) -> None:
        if not fulfilled:
            return

        self._logger.info(
            f"Fulfilled targets: {', '.join(f'{tp.symbol}@{tp.target}' for tp in fulfilled)}"
        )
        fulfilled_pairs = {(tp.symbol, tp.target) for tp in fulfilled}
        updated_symbols = [
            SymbolConfig(
                symbol=sc.symbol,
                prices=[p for p in sc.prices if (sc.symbol, p) not in fulfilled_pairs],
            )
            for sc in self._config.symbols
        ]

        if updated_symbols == self._config.symbols:
            return

        new_config = MonitorStocksConfig(
            interval=self._config.interval,
            symbols=updated_symbols,
        )
        self._config = new_config
        self._config_manager.write_monitor_stocks_config(new_config)
        self._logger.info("Removing fulfilled targets from config.")
        self.log_config()

    def log_config(self) -> None:
        self._logger.info(f"Monitoring every {self._config.interval}s.")
        stocks_info = [
            f"{s.symbol} @ {', '.join(str(p) for p in s.prices)}" if s.prices else s.symbol
            for s in self._config.symbols
        ]
        self._logger.info(f"Stocks: {' | '.join(stocks_info)}")

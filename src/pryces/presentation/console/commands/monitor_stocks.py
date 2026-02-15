import logging
import time

from ....application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
)
from .base import Command, CommandMetadata, InputPrompt
from ..utils import parse_symbols_input, validate_positive_integer, validate_symbols


class MonitorStocksCommand(Command):
    def __init__(self, trigger_stocks_notifications_use_case: TriggerStocksNotifications) -> None:
        self._trigger_stocks_notifications = trigger_stocks_notifications_use_case
        self._logger = logging.getLogger(__name__)

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="monitor_stocks",
            name="Monitor Stocks",
            description="Monitor stocks for relevant price notifications",
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return [
            InputPrompt(
                key="symbols",
                prompt="Enter stock symbols separated by commas (e.g., AAPL,GOOGL,MSFT): ",
                validator=validate_symbols,
            ),
            InputPrompt(
                key="interval",
                prompt="Enter interval between checks in seconds (e.g., 90): ",
                validator=validate_positive_integer,
            ),
            InputPrompt(
                key="duration",
                prompt="Enter monitoring duration in minutes (e.g., 120): ",
                validator=validate_positive_integer,
            ),
        ]

    def execute(
        self, symbols: str = None, interval: str = None, duration: str = None, **kwargs
    ) -> str:
        self._logger.info("Monitor Stocks command started")
        interval_seconds = int(interval)
        duration_seconds = int(duration) * 60

        symbol_list = parse_symbols_input(symbols)
        request = TriggerStocksNotificationsRequest(symbols=symbol_list)

        start = time.monotonic()

        while True:
            try:
                self._trigger_stocks_notifications.handle(request)
            except Exception as e:
                self._logger.warning(f"Exception caught: {e}")

            if time.monotonic() - start >= duration_seconds:
                break

            time.sleep(interval_seconds)

        self._logger.info("Monitor Stocks command finished")
        return (
            f"Monitoring complete. {len(symbol_list)} stocks checked " f"over {duration} minutes."
        )

import time

from ....application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
)
from .base import Command, CommandMetadata, InputPrompt


def validate_symbols(value: str) -> bool:
    if not value or not value.strip():
        return False

    symbols = [s.strip() for s in value.split(",")]
    return all(symbol and len(symbol) <= 10 for symbol in symbols)


def validate_positive_integer(value: str) -> bool:
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False


def parse_symbols_input(value: str) -> list[str]:
    symbols = [s.strip().upper() for s in value.split(",")]
    return [s for s in symbols if s]


class MonitorStocksCommand(Command):
    def __init__(self, trigger_stocks_notifications_use_case: TriggerStocksNotifications) -> None:
        self._trigger_stocks_notifications = trigger_stocks_notifications_use_case

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
                key="repetitions",
                prompt="Enter number of repetitions (e.g., 525): ",
                validator=validate_positive_integer,
            ),
        ]

    def execute(
        self, symbols: str = None, interval: str = None, repetitions: str = None, **kwargs
    ) -> str:
        interval_seconds = int(interval)
        repetition_count = int(repetitions)

        try:
            symbol_list = parse_symbols_input(symbols)
            request = TriggerStocksNotificationsRequest(symbols=symbol_list)

            total_notifications = 0

            for i in range(repetition_count):
                notifications = self._trigger_stocks_notifications.handle(request)
                total_notifications += len(notifications)

                if i < repetition_count - 1:
                    time.sleep(interval_seconds)

            return (
                f"Monitoring complete. {len(symbol_list)} stocks checked, "
                f"{total_notifications} notifications sent over {repetition_count} repetitions."
            )

        except Exception as e:
            return f"Monitoring failed: {e}"

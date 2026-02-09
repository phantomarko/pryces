import logging

from ....application.use_cases.trigger_stocks_notifications import (
    TriggerStocksNotifications,
    TriggerStocksNotificationsRequest,
    TriggerType,
)
from .base import Command, CommandMetadata, InputPrompt


def validate_symbols(value: str) -> bool:
    if not value or not value.strip():
        return False

    symbols = [s.strip() for s in value.split(",")]
    return all(symbol and len(symbol) <= 10 for symbol in symbols)


def parse_symbols_input(value: str) -> list[str]:
    symbols = [s.strip().upper() for s in value.split(",")]
    return [s for s in symbols if s]


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
            )
        ]

    def execute(self, symbols: str = None, **kwargs) -> str:
        self._logger.info(f"Monitoring stocks for notifications: {symbols}")

        try:
            symbol_list = parse_symbols_input(symbols)
            request = TriggerStocksNotificationsRequest(
                type=TriggerType.MILESTONES, symbols=symbol_list
            )
            notifications = self._trigger_stocks_notifications.handle(request)

            for notification in notifications:
                self._logger.info(f"Notification: {notification.message}")

            self._logger.info(
                f"Monitoring complete: {len(symbol_list)} stocks checked, "
                f"{len(notifications)} notifications sent"
            )

            return (
                f"Monitoring complete. {len(symbol_list)} stocks checked, "
                f"{len(notifications)} notifications sent."
            )

        except Exception as e:
            self._logger.exception(f"Unexpected error while monitoring stocks for {symbols}")
            return f"Monitoring failed: {e}"

import logging

from ....application.use_cases.send_messages import SendMessages, SendMessagesRequest
from .base import Command, CommandMetadata, InputPrompt


class SendMessagesCommand(Command):
    def __init__(self, send_messages_use_case: SendMessages) -> None:
        self._send_messages = send_messages_use_case
        self._logger = logging.getLogger(__name__)

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="send_messages",
            name="Test Notifications",
            description="Send a test notification message",
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return []

    def execute(self, **kwargs) -> str:
        self._logger.info("Send Messages command started")
        try:
            request = SendMessagesRequest(messages=["Hello!\nThis is a test message."])
            response = self._send_messages.handle(request)

            self._logger.info("Send Messages command finished")
            if response.successful > 0 and response.failed == 0:
                return "Test notification sent successfully."
            else:
                return "Test notification failed."

        except Exception as e:
            self._logger.error(f"Send Messages command finished with errors: {e}")
            return f"Test notification failed: {e}"

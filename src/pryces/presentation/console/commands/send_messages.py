from ....application.use_cases.send_messages import SendMessages, SendMessagesRequest
from .base import Command, CommandMetadata, InputPrompt


class SendMessagesCommand(Command):
    def __init__(self, send_messages_use_case: SendMessages) -> None:
        self._send_messages = send_messages_use_case

    def get_metadata(self) -> CommandMetadata:
        return CommandMetadata(
            id="send_messages",
            name="Test Notifications",
            description="Send a test notification message",
        )

    def get_input_prompts(self) -> list[InputPrompt]:
        return []

    def execute(self, **kwargs) -> str:
        try:
            request = SendMessagesRequest(messages=["This is a test message"])
            response = self._send_messages.handle(request)

            if response.successful > 0 and response.failed == 0:
                return "Test notification sent successfully."
            else:
                return "Test notification failed."

        except Exception as e:
            return f"Test notification failed: {e}"

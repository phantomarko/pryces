from unittest.mock import Mock

from pryces.application.interfaces import MessageSender
from pryces.application.use_cases.send_messages import SendMessages
from pryces.presentation.console.commands.send_messages import SendMessagesCommand
from pryces.presentation.console.commands.base import CommandMetadata


class TestSendMessagesCommand:

    def setup_method(self):
        self.mock_sender = Mock(spec=MessageSender)
        use_case = SendMessages(sender=self.mock_sender)
        self.command = SendMessagesCommand(use_case)

    def test_get_metadata_returns_correct_metadata(self):
        metadata = self.command.get_metadata()

        assert isinstance(metadata, CommandMetadata)
        assert metadata.id == "send_messages"
        assert metadata.name == "Test Notifications"
        assert metadata.description == "Send a test notification message"

    def test_get_input_prompts_returns_empty_list(self):
        prompts = self.command.get_input_prompts()

        assert prompts == []

    def test_execute_returns_success_message_when_notification_sent(self):
        self.mock_sender.send_message.return_value = True

        result = self.command.execute()

        assert result == "Test notification sent successfully."

    def test_execute_returns_failure_message_when_notification_fails(self):
        self.mock_sender.send_message.return_value = False

        result = self.command.execute()

        assert result == "Test notification failed."

    def test_execute_handles_unexpected_exception(self):
        self.mock_sender.send_message.side_effect = Exception("Connection error")

        result = self.command.execute()

        assert result == "Test notification failed: Connection error"

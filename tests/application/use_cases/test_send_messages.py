from unittest.mock import Mock

from pryces.application.messages import MessageSender
from pryces.application.use_cases.send_messages import (
    SendMessages,
    SendMessagesRequest,
    SendMessagesResponse,
)


class TestSendMessages:

    def setup_method(self):
        self.mock_sender = Mock(spec=MessageSender)

    def test_handle_counts_all_successful_messages(self):
        self.mock_sender.send_message.return_value = True
        request = SendMessagesRequest(messages=["msg1", "msg2", "msg3"])
        use_case = SendMessages(sender=self.mock_sender)

        result = use_case.handle(request)

        assert result == SendMessagesResponse(successful=3, failed=0)
        assert self.mock_sender.send_message.call_count == 3

    def test_handle_counts_false_returns_as_failures(self):
        self.mock_sender.send_message.return_value = False
        request = SendMessagesRequest(messages=["msg1", "msg2"])
        use_case = SendMessages(sender=self.mock_sender)

        result = use_case.handle(request)

        assert result == SendMessagesResponse(successful=0, failed=2)

    def test_handle_counts_exceptions_as_failures(self):
        self.mock_sender.send_message.side_effect = RuntimeError("connection lost")
        request = SendMessagesRequest(messages=["msg1"])
        use_case = SendMessages(sender=self.mock_sender)

        result = use_case.handle(request)

        assert result == SendMessagesResponse(successful=0, failed=1)

    def test_handle_continues_after_exception(self):
        self.mock_sender.send_message.side_effect = [
            RuntimeError("fail"),
            True,
            True,
        ]
        request = SendMessagesRequest(messages=["msg1", "msg2", "msg3"])
        use_case = SendMessages(sender=self.mock_sender)

        result = use_case.handle(request)

        assert result == SendMessagesResponse(successful=2, failed=1)
        assert self.mock_sender.send_message.call_count == 3

    def test_handle_returns_zero_counts_for_empty_list(self):
        request = SendMessagesRequest(messages=[])
        use_case = SendMessages(sender=self.mock_sender)

        result = use_case.handle(request)

        assert result == SendMessagesResponse(successful=0, failed=0)
        self.mock_sender.send_message.assert_not_called()

    def test_handle_counts_all_messages_as_failed(self):
        self.mock_sender.send_message.side_effect = [False, RuntimeError("err"), False]
        request = SendMessagesRequest(messages=["msg1", "msg2", "msg3"])
        use_case = SendMessages(sender=self.mock_sender)

        result = use_case.handle(request)

        assert result == SendMessagesResponse(successful=0, failed=3)

    def test_handle_counts_mixed_false_and_exception_failures(self):
        self.mock_sender.send_message.side_effect = [
            True,
            False,
            RuntimeError("timeout"),
            True,
        ]
        request = SendMessagesRequest(messages=["msg1", "msg2", "msg3", "msg4"])
        use_case = SendMessages(sender=self.mock_sender)

        result = use_case.handle(request)

        assert result == SendMessagesResponse(successful=2, failed=2)

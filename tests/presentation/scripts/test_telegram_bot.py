from unittest.mock import Mock, call

from pryces.application.use_cases.send_messages import SendMessages, SendMessagesRequest
from pryces.infrastructure.receivers import BotUpdate, TelegramUpdatePoller
from pryces.presentation.scripts.bot_commands import BotCommandDispatcher
from pryces.presentation.scripts.telegram_bot import TelegramBotScript


def make_script(
    poller=None,
    send_messages=None,
    dispatcher=None,
    group_id="123",
) -> TelegramBotScript:
    return TelegramBotScript(
        poller=poller or Mock(spec=TelegramUpdatePoller),
        send_messages=send_messages or Mock(spec=SendMessages),
        dispatcher=dispatcher or Mock(spec=BotCommandDispatcher),
        group_id=group_id,
        logger_factory=Mock(),
    )


class TestTelegramBotScript:

    def test_sends_reply_for_matching_chat_id(self):
        poller = Mock(spec=TelegramUpdatePoller)
        updates = [BotUpdate(update_id=1, chat_id="123", text="/help")]
        poller.get_updates.side_effect = [updates, KeyboardInterrupt]
        send_messages = Mock(spec=SendMessages)
        dispatcher = Mock(spec=BotCommandDispatcher)
        dispatcher.dispatch.return_value = "help text"

        script = make_script(poller=poller, send_messages=send_messages, dispatcher=dispatcher)

        try:
            script.run()
        except KeyboardInterrupt:
            pass

        dispatcher.dispatch.assert_called_once_with("/help")
        send_messages.handle.assert_called_once_with(SendMessagesRequest(messages=["help text"]))

    def test_skips_updates_from_foreign_chat_id(self):
        poller = Mock(spec=TelegramUpdatePoller)
        updates = [BotUpdate(update_id=1, chat_id="999", text="/help")]
        poller.get_updates.side_effect = [updates, KeyboardInterrupt]
        send_messages = Mock(spec=SendMessages)
        dispatcher = Mock(spec=BotCommandDispatcher)

        script = make_script(poller=poller, send_messages=send_messages, dispatcher=dispatcher)

        try:
            script.run()
        except KeyboardInterrupt:
            pass

        dispatcher.dispatch.assert_not_called()
        send_messages.handle.assert_not_called()

    def test_does_not_send_when_dispatch_returns_empty(self):
        poller = Mock(spec=TelegramUpdatePoller)
        updates = [BotUpdate(update_id=1, chat_id="123", text="hello")]
        poller.get_updates.side_effect = [updates, KeyboardInterrupt]
        send_messages = Mock(spec=SendMessages)
        dispatcher = Mock(spec=BotCommandDispatcher)
        dispatcher.dispatch.return_value = ""

        script = make_script(poller=poller, send_messages=send_messages, dispatcher=dispatcher)

        try:
            script.run()
        except KeyboardInterrupt:
            pass

        send_messages.handle.assert_not_called()

    def test_advances_offset_correctly(self):
        poller = Mock(spec=TelegramUpdatePoller)
        batch1 = [
            BotUpdate(update_id=10, chat_id="123", text="/help"),
            BotUpdate(update_id=11, chat_id="123", text="/help"),
        ]
        poller.get_updates.side_effect = [batch1, KeyboardInterrupt]
        dispatcher = Mock(spec=BotCommandDispatcher)
        dispatcher.dispatch.return_value = ""

        script = make_script(poller=poller, dispatcher=dispatcher)

        try:
            script.run()
        except KeyboardInterrupt:
            pass

        assert poller.get_updates.call_args_list[0] == call(0)
        assert poller.get_updates.call_args_list[1] == call(12)

    def test_continues_on_send_message_error(self):
        poller = Mock(spec=TelegramUpdatePoller)
        updates = [
            BotUpdate(update_id=1, chat_id="123", text="/help"),
            BotUpdate(update_id=2, chat_id="123", text="/help"),
        ]
        poller.get_updates.side_effect = [updates, KeyboardInterrupt]
        send_messages = Mock(spec=SendMessages)
        send_messages.handle.side_effect = [Exception("send failed"), None]
        dispatcher = Mock(spec=BotCommandDispatcher)
        dispatcher.dispatch.return_value = "reply"

        script = make_script(poller=poller, send_messages=send_messages, dispatcher=dispatcher)

        try:
            script.run()
        except KeyboardInterrupt:
            pass

        assert send_messages.handle.call_count == 2

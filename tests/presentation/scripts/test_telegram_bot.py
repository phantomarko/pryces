from unittest.mock import Mock, call, patch

from pryces.infrastructure.receivers import BotUpdate, TelegramUpdatePoller
from pryces.presentation.scripts.bot_commands import BotCommandDispatcher
from pryces.presentation.scripts.telegram_bot import TelegramBotScript


def make_script(
    poller=None,
    message_sender=None,
    dispatcher=None,
    group_id="123",
) -> TelegramBotScript:
    return TelegramBotScript(
        poller=poller or Mock(spec=TelegramUpdatePoller),
        message_sender=message_sender or Mock(),
        dispatcher=dispatcher or Mock(spec=BotCommandDispatcher),
        group_id=group_id,
        logger_factory=Mock(),
    )


class TestTelegramBotScript:

    def test_sends_reply_for_matching_chat_id(self):
        poller = Mock(spec=TelegramUpdatePoller)
        updates = [BotUpdate(update_id=1, chat_id="123", text="/help")]
        poller.get_updates.side_effect = [updates, KeyboardInterrupt]
        sender = Mock()
        dispatcher = Mock(spec=BotCommandDispatcher)
        dispatcher.dispatch.return_value = "help text"

        script = make_script(poller=poller, message_sender=sender, dispatcher=dispatcher)

        try:
            script.run()
        except KeyboardInterrupt:
            pass

        dispatcher.dispatch.assert_called_once_with("/help")
        sender.send_message.assert_called_once_with("help text")

    def test_skips_updates_from_foreign_chat_id(self):
        poller = Mock(spec=TelegramUpdatePoller)
        updates = [BotUpdate(update_id=1, chat_id="999", text="/help")]
        poller.get_updates.side_effect = [updates, KeyboardInterrupt]
        sender = Mock()
        dispatcher = Mock(spec=BotCommandDispatcher)

        script = make_script(poller=poller, message_sender=sender, dispatcher=dispatcher)

        try:
            script.run()
        except KeyboardInterrupt:
            pass

        dispatcher.dispatch.assert_not_called()
        sender.send_message.assert_not_called()

    def test_does_not_send_when_dispatch_returns_empty(self):
        poller = Mock(spec=TelegramUpdatePoller)
        updates = [BotUpdate(update_id=1, chat_id="123", text="hello")]
        poller.get_updates.side_effect = [updates, KeyboardInterrupt]
        sender = Mock()
        dispatcher = Mock(spec=BotCommandDispatcher)
        dispatcher.dispatch.return_value = ""

        script = make_script(poller=poller, message_sender=sender, dispatcher=dispatcher)

        try:
            script.run()
        except KeyboardInterrupt:
            pass

        sender.send_message.assert_not_called()

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
        sender = Mock()
        sender.send_message.side_effect = [Exception("send failed"), True]
        dispatcher = Mock(spec=BotCommandDispatcher)
        dispatcher.dispatch.return_value = "reply"

        script = make_script(poller=poller, message_sender=sender, dispatcher=dispatcher)

        try:
            script.run()
        except KeyboardInterrupt:
            pass

        assert sender.send_message.call_count == 2

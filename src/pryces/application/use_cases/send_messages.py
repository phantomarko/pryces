from dataclasses import dataclass

from ..messages import MessageSender


@dataclass(frozen=True)
class SendMessagesRequest:
    messages: list[str]


@dataclass(frozen=True)
class SendMessagesResponse:
    successful: int
    failed: int


class SendMessages:
    def __init__(self, sender: MessageSender) -> None:
        self._sender = sender

    def handle(self, request: SendMessagesRequest) -> SendMessagesResponse:
        successful = 0
        failed = 0

        for message in request.messages:
            try:
                if self._sender.send_message(message):
                    successful += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

        return SendMessagesResponse(successful=successful, failed=failed)

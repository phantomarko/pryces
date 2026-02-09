from pryces.domain.notifications import Notification
from pryces.domain.stocks import Stock

from .interfaces import MessageSender


class NotificationService:
    def __init__(self, message_sender: MessageSender) -> None:
        self._message_sender = message_sender
        self._notifications_sent: dict[str, list[Notification]] = {}

    @property
    def notifications_sent(self) -> dict[str, list[Notification]]:
        return self._notifications_sent

    def send_stock_notifications(self, stock: Stock) -> list[Notification]:
        sent: list[Notification] = []

        for notification in stock.notifications:
            if self._already_sent(stock.symbol, notification):
                continue

            self._message_sender.send_message(notification.message)

            if stock.symbol not in self._notifications_sent:
                self._notifications_sent[stock.symbol] = []
            self._notifications_sent[stock.symbol].append(notification)
            sent.append(notification)

        return sent

    def _already_sent(self, symbol: str, notification: Notification) -> bool:
        if symbol not in self._notifications_sent:
            return False
        return any(notification.equals(sent) for sent in self._notifications_sent[symbol])

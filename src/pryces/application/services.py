from pryces.domain.notifications import Notification
from pryces.domain.stocks import Stock

from .interfaces import MessageSender, NotificationRepository


class NotificationService:
    def __init__(self, message_sender: MessageSender, repository: NotificationRepository) -> None:
        self._message_sender = message_sender
        self._repository = repository

    def send_stock_notifications(self, stock: Stock) -> list[Notification]:
        stock.generate_notifications()
        sent: list[Notification] = []

        for notification in stock.notifications:
            if self._repository.exists_by_type(stock.symbol, notification.type):
                continue

            self._message_sender.send_message(notification.message)
            self._repository.save(stock.symbol, notification)
            sent.append(notification)

        return sent

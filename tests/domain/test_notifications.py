from decimal import Decimal

import pytest

from pryces.domain.notifications import Notification, NotificationType


def test_cannot_create_notification_directly():
    with pytest.raises(TypeError):
        Notification(object(), NotificationType.SMA50_CROSSED, "some message")


def test_create_fifty_day_average_crossed_sets_type():
    notification = Notification.create_fifty_day_average_crossed(
        "AAPL", Decimal("150.00"), Decimal("145.00")
    )

    assert notification.type == NotificationType.SMA50_CROSSED


def test_create_fifty_day_average_crossed_sets_message():
    notification = Notification.create_fifty_day_average_crossed(
        "AAPL", Decimal("150.00"), Decimal("145.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_two_hundred_day_average_crossed_sets_type():
    notification = Notification.create_two_hundred_day_average_crossed(
        "AAPL", Decimal("150.00"), Decimal("140.00")
    )

    assert notification.type == NotificationType.SMA200_CROSSED


def test_create_two_hundred_day_average_crossed_sets_message():
    notification = Notification.create_two_hundred_day_average_crossed(
        "AAPL", Decimal("150.00"), Decimal("140.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_notification_type_enum_has_expected_values():
    assert NotificationType.SMA50_CROSSED.value == "SMA50_CROSSED"
    assert NotificationType.SMA200_CROSSED.value == "SMA200_CROSSED"

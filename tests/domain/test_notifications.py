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


def test_equals_returns_true_for_same_type():
    notification1 = Notification.create_fifty_day_average_crossed(
        "AAPL", Decimal("150.00"), Decimal("145.00")
    )
    notification2 = Notification.create_fifty_day_average_crossed(
        "GOOGL", Decimal("200.00"), Decimal("190.00")
    )

    assert notification1.equals(notification2) is True


def test_equals_returns_false_for_different_type():
    notification1 = Notification.create_fifty_day_average_crossed(
        "AAPL", Decimal("150.00"), Decimal("145.00")
    )
    notification2 = Notification.create_two_hundred_day_average_crossed(
        "AAPL", Decimal("150.00"), Decimal("140.00")
    )

    assert notification1.equals(notification2) is False


def test_create_regular_market_open_sets_type():
    notification = Notification.create_regular_market_open("AAPL", Decimal("150.00"), None)

    assert notification.type == NotificationType.REGULAR_MARKET_OPEN


def test_create_regular_market_open_sets_message():
    notification = Notification.create_regular_market_open("AAPL", Decimal("150.00"), None)

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_regular_market_open_with_last_close_price_sets_type():
    notification = Notification.create_regular_market_open(
        "AAPL", Decimal("150.00"), Decimal("148.00")
    )

    assert notification.type == NotificationType.REGULAR_MARKET_OPEN


def test_create_regular_market_open_with_last_close_price_sets_message():
    notification = Notification.create_regular_market_open(
        "AAPL", Decimal("150.00"), Decimal("148.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_regular_market_closed_sets_type():
    notification = Notification.create_regular_market_closed("AAPL", Decimal("150.00"), None)

    assert notification.type == NotificationType.REGULAR_MARKET_CLOSED


def test_create_regular_market_closed_sets_message():
    notification = Notification.create_regular_market_closed("AAPL", Decimal("150.00"), None)

    assert isinstance(notification.message, str)
    assert "150.00" in notification.message


def test_create_regular_market_closed_with_last_day_price_sets_type():
    notification = Notification.create_regular_market_closed(
        "AAPL", Decimal("150.00"), Decimal("148.00")
    )

    assert notification.type == NotificationType.REGULAR_MARKET_CLOSED


def test_create_regular_market_closed_with_last_day_price_sets_message():
    notification = Notification.create_regular_market_closed(
        "AAPL", Decimal("150.00"), Decimal("148.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_five_percent_increase_sets_type():
    notification = Notification.create_five_percent_increase(
        "AAPL", Decimal("157.50"), Decimal("5.00")
    )

    assert notification.type == NotificationType.FIVE_PERCENT_INCREASE


def test_create_five_percent_increase_sets_message():
    notification = Notification.create_five_percent_increase(
        "AAPL", Decimal("157.50"), Decimal("5.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_ten_percent_increase_sets_type():
    notification = Notification.create_ten_percent_increase(
        "AAPL", Decimal("165.00"), Decimal("10.00")
    )

    assert notification.type == NotificationType.TEN_PERCENT_INCREASE


def test_create_ten_percent_increase_sets_message():
    notification = Notification.create_ten_percent_increase(
        "AAPL", Decimal("165.00"), Decimal("10.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_fifteen_percent_increase_sets_type():
    notification = Notification.create_fifteen_percent_increase(
        "AAPL", Decimal("172.50"), Decimal("15.00")
    )

    assert notification.type == NotificationType.FIFTEEN_PERCENT_INCREASE


def test_create_fifteen_percent_increase_sets_message():
    notification = Notification.create_fifteen_percent_increase(
        "AAPL", Decimal("172.50"), Decimal("15.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_twenty_percent_increase_sets_type():
    notification = Notification.create_twenty_percent_increase(
        "AAPL", Decimal("180.00"), Decimal("20.00")
    )

    assert notification.type == NotificationType.TWENTY_PERCENT_INCREASE


def test_create_twenty_percent_increase_sets_message():
    notification = Notification.create_twenty_percent_increase(
        "AAPL", Decimal("180.00"), Decimal("20.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_five_percent_decrease_sets_type():
    notification = Notification.create_five_percent_decrease(
        "AAPL", Decimal("142.50"), Decimal("-5.00")
    )

    assert notification.type == NotificationType.FIVE_PERCENT_DECREASE


def test_create_five_percent_decrease_sets_message():
    notification = Notification.create_five_percent_decrease(
        "AAPL", Decimal("142.50"), Decimal("-5.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_ten_percent_decrease_sets_type():
    notification = Notification.create_ten_percent_decrease(
        "AAPL", Decimal("135.00"), Decimal("-10.00")
    )

    assert notification.type == NotificationType.TEN_PERCENT_DECREASE


def test_create_ten_percent_decrease_sets_message():
    notification = Notification.create_ten_percent_decrease(
        "AAPL", Decimal("135.00"), Decimal("-10.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_fifteen_percent_decrease_sets_type():
    notification = Notification.create_fifteen_percent_decrease(
        "AAPL", Decimal("127.50"), Decimal("-15.00")
    )

    assert notification.type == NotificationType.FIFTEEN_PERCENT_DECREASE


def test_create_fifteen_percent_decrease_sets_message():
    notification = Notification.create_fifteen_percent_decrease(
        "AAPL", Decimal("127.50"), Decimal("-15.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_twenty_percent_decrease_sets_type():
    notification = Notification.create_twenty_percent_decrease(
        "AAPL", Decimal("120.00"), Decimal("-20.00")
    )

    assert notification.type == NotificationType.TWENTY_PERCENT_DECREASE


def test_create_twenty_percent_decrease_sets_message():
    notification = Notification.create_twenty_percent_decrease(
        "AAPL", Decimal("120.00"), Decimal("-20.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_notification_type_enum_has_expected_values():
    assert NotificationType.SMA50_CROSSED.value == "SMA50_CROSSED"
    assert NotificationType.SMA200_CROSSED.value == "SMA200_CROSSED"
    assert NotificationType.REGULAR_MARKET_OPEN.value == "REGULAR_MARKET_OPEN"
    assert NotificationType.REGULAR_MARKET_CLOSED.value == "REGULAR_MARKET_CLOSED"
    assert NotificationType.FIVE_PERCENT_INCREASE.value == "FIVE_PERCENT_INCREASE"
    assert NotificationType.TEN_PERCENT_INCREASE.value == "TEN_PERCENT_INCREASE"
    assert NotificationType.FIFTEEN_PERCENT_INCREASE.value == "FIFTEEN_PERCENT_INCREASE"
    assert NotificationType.TWENTY_PERCENT_INCREASE.value == "TWENTY_PERCENT_INCREASE"
    assert NotificationType.FIVE_PERCENT_DECREASE.value == "FIVE_PERCENT_DECREASE"
    assert NotificationType.TEN_PERCENT_DECREASE.value == "TEN_PERCENT_DECREASE"
    assert NotificationType.FIFTEEN_PERCENT_DECREASE.value == "FIFTEEN_PERCENT_DECREASE"
    assert NotificationType.TWENTY_PERCENT_DECREASE.value == "TWENTY_PERCENT_DECREASE"

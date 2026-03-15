from decimal import Decimal

import pytest

from pryces.domain.notifications import Notification, NotificationType


def test_cannot_create_notification_directly():
    with pytest.raises(TypeError):
        Notification(object(), NotificationType.SMA50_CROSSED, "some message")


def test_create_fifty_day_average_crossed_sets_type():
    notification = Notification.create_fifty_day_average_crossed(
        "AAPL", Decimal("150.00"), Decimal("1.25"), Decimal("145.00")
    )

    assert notification.type == NotificationType.SMA50_CROSSED


def test_create_fifty_day_average_crossed_sets_message():
    notification = Notification.create_fifty_day_average_crossed(
        "AAPL", Decimal("150.00"), Decimal("1.25"), Decimal("145.00")
    )

    assert "AAPL rose to 150.00 (+1.25%)" in notification.message
    assert "crossed SMA50 at 145.00" in notification.message


def test_create_two_hundred_day_average_crossed_sets_type():
    notification = Notification.create_two_hundred_day_average_crossed(
        "AAPL", Decimal("138.00"), Decimal("-1.50"), Decimal("140.00")
    )

    assert notification.type == NotificationType.SMA200_CROSSED


def test_create_two_hundred_day_average_crossed_sets_message():
    notification = Notification.create_two_hundred_day_average_crossed(
        "AAPL", Decimal("138.00"), Decimal("-1.50"), Decimal("140.00")
    )

    assert "AAPL dropped to 138.00 (-1.50%)" in notification.message
    assert "crossed SMA200 at 140.00" in notification.message


def test_create_close_to_fifty_day_average_sets_type():
    notification = Notification.create_close_to_fifty_day_average(
        "AAPL", Decimal("100.00"), Decimal("10.00"), Decimal("103.00")
    )

    assert notification.type == NotificationType.CLOSE_TO_SMA50


def test_create_fifty_day_average_crossed_sets_message_with_zero_change():
    notification = Notification.create_fifty_day_average_crossed(
        "AAPL", Decimal("150.00"), Decimal("0"), Decimal("150.00")
    )

    assert "AAPL at 150.00 (+0.00%)" in notification.message


def test_create_close_to_fifty_day_average_sets_below_direction():
    notification = Notification.create_close_to_fifty_day_average(
        "AAPL", Decimal("100.00"), Decimal("10.00"), Decimal("103.00")
    )

    assert "below SMA50 at" in notification.message


def test_create_close_to_fifty_day_average_sets_above_direction():
    notification = Notification.create_close_to_fifty_day_average(
        "AAPL", Decimal("105.00"), Decimal("10.00"), Decimal("103.00")
    )

    assert "above SMA50 at" in notification.message


def test_create_close_to_two_hundred_day_average_sets_type():
    notification = Notification.create_close_to_two_hundred_day_average(
        "AAPL", Decimal("100.00"), Decimal("-10.00"), Decimal("103.00")
    )

    assert notification.type == NotificationType.CLOSE_TO_SMA200


def test_create_close_to_two_hundred_day_average_sets_below_direction():
    notification = Notification.create_close_to_two_hundred_day_average(
        "AAPL", Decimal("100.00"), Decimal("-10.00"), Decimal("103.00")
    )

    assert "below SMA200 at" in notification.message


def test_create_close_to_two_hundred_day_average_sets_above_direction():
    notification = Notification.create_close_to_two_hundred_day_average(
        "AAPL", Decimal("105.00"), Decimal("-10.00"), Decimal("103.00")
    )

    assert "above SMA200 at" in notification.message


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


def test_create_percentage_change_sets_type():
    notification = Notification.create_percentage_change(
        NotificationType.LEVEL_1_INCREASE, "AAPL", Decimal("157.50"), Decimal("5.00")
    )

    assert notification.type == NotificationType.LEVEL_1_INCREASE


def test_create_percentage_change_sets_message():
    notification = Notification.create_percentage_change(
        NotificationType.LEVEL_1_INCREASE, "AAPL", Decimal("157.50"), Decimal("5.00")
    )

    assert isinstance(notification.message, str)
    assert len(notification.message) > 0


def test_create_percentage_change_formats_increase_message():
    notification = Notification.create_percentage_change(
        NotificationType.LEVEL_2_INCREASE, "AAPL", Decimal("165.00"), Decimal("10.00")
    )

    assert "AAPL rose to 165.00 (+10.00%)" == notification.message


def test_create_percentage_change_formats_decrease_message():
    notification = Notification.create_percentage_change(
        NotificationType.LEVEL_2_DECREASE, "AAPL", Decimal("135.00"), Decimal("-10.00")
    )

    assert "AAPL dropped to 135.00 (-10.00%)" == notification.message


def test_create_percentage_change_preserves_notification_type():
    for notification_type in [
        NotificationType.LEVEL_1_INCREASE,
        NotificationType.LEVEL_2_INCREASE,
        NotificationType.LEVEL_3_INCREASE,
        NotificationType.LEVEL_4_INCREASE,
        NotificationType.LEVEL_5_INCREASE,
        NotificationType.LEVEL_1_DECREASE,
        NotificationType.LEVEL_2_DECREASE,
        NotificationType.LEVEL_3_DECREASE,
        NotificationType.LEVEL_4_DECREASE,
        NotificationType.LEVEL_5_DECREASE,
    ]:
        notification = Notification.create_percentage_change(
            notification_type, "AAPL", Decimal("150.00"), Decimal("5.00")
        )
        assert notification.type == notification_type


def test_create_new_52_week_high_sets_type():
    notification = Notification.create_new_52_week_high("AAPL", Decimal("225.50"), Decimal("5.00"))

    assert notification.type == NotificationType.NEW_52_WEEK_HIGH


def test_create_new_52_week_high_sets_message():
    notification = Notification.create_new_52_week_high("AAPL", Decimal("225.50"), Decimal("5.00"))

    assert notification.message == "AAPL rose to 225.50 (+5.00%), hit a new 52-week high"


def test_create_new_52_week_low_sets_type():
    notification = Notification.create_new_52_week_low("AAPL", Decimal("142.30"), Decimal("-3.50"))

    assert notification.type == NotificationType.NEW_52_WEEK_LOW


def test_create_new_52_week_low_sets_message():
    notification = Notification.create_new_52_week_low("AAPL", Decimal("142.30"), Decimal("-3.50"))

    assert notification.message == "AAPL dropped to 142.30 (-3.50%), hit a new 52-week low"


def test_create_target_price_reached_sets_type():
    notification = Notification.create_target_price_reached("AAPL", Decimal("200.00"))

    assert notification.type == NotificationType.TARGET_PRICE_REACHED


def test_create_target_price_reached_sets_message():
    notification = Notification.create_target_price_reached("AAPL", Decimal("200.00"))

    assert "AAPL" in notification.message
    assert "target of" in notification.message
    assert "200.00" in notification.message


def test_create_session_gains_erased_sets_type():
    notification = Notification.create_session_gains_erased("AAPL", Decimal("10"), Decimal("-1.54"))

    assert notification.type == NotificationType.SESSION_GAINS_ERASED


def test_create_session_gains_erased_sets_message():
    notification = Notification.create_session_gains_erased("AAPL", Decimal("10"), Decimal("-1.54"))

    assert "AAPL dropped to 10 (-1.54%)" in notification.message
    assert "erased the session gains" in notification.message


def test_create_session_losses_erased_sets_type():
    notification = Notification.create_session_losses_erased("AAPL", Decimal("10"), Decimal("0.54"))

    assert notification.type == NotificationType.SESSION_LOSSES_ERASED


def test_create_session_losses_erased_sets_message():
    notification = Notification.create_session_losses_erased("AAPL", Decimal("10"), Decimal("0.54"))

    assert "AAPL rose to 10 (+0.54%)" in notification.message
    assert "erased the session losses" in notification.message


def test_notification_type_enum_has_expected_values():
    assert NotificationType.SMA50_CROSSED.value == "SMA50_CROSSED"
    assert NotificationType.SMA200_CROSSED.value == "SMA200_CROSSED"
    assert NotificationType.CLOSE_TO_SMA50.value == "CLOSE_TO_SMA50"
    assert NotificationType.CLOSE_TO_SMA200.value == "CLOSE_TO_SMA200"
    assert NotificationType.REGULAR_MARKET_OPEN.value == "REGULAR_MARKET_OPEN"
    assert NotificationType.REGULAR_MARKET_CLOSED.value == "REGULAR_MARKET_CLOSED"
    assert NotificationType.LEVEL_1_INCREASE.value == "LEVEL_1_INCREASE"
    assert NotificationType.LEVEL_2_INCREASE.value == "LEVEL_2_INCREASE"
    assert NotificationType.LEVEL_3_INCREASE.value == "LEVEL_3_INCREASE"
    assert NotificationType.LEVEL_4_INCREASE.value == "LEVEL_4_INCREASE"
    assert NotificationType.LEVEL_5_INCREASE.value == "LEVEL_5_INCREASE"
    assert NotificationType.LEVEL_1_DECREASE.value == "LEVEL_1_DECREASE"
    assert NotificationType.LEVEL_2_DECREASE.value == "LEVEL_2_DECREASE"
    assert NotificationType.LEVEL_3_DECREASE.value == "LEVEL_3_DECREASE"
    assert NotificationType.LEVEL_4_DECREASE.value == "LEVEL_4_DECREASE"
    assert NotificationType.LEVEL_5_DECREASE.value == "LEVEL_5_DECREASE"
    assert NotificationType.SESSION_GAINS_ERASED.value == "SESSION_GAINS_ERASED"
    assert NotificationType.SESSION_LOSSES_ERASED.value == "SESSION_LOSSES_ERASED"
    assert NotificationType.NEW_52_WEEK_HIGH.value == "NEW_52_WEEK_HIGH"
    assert NotificationType.NEW_52_WEEK_LOW.value == "NEW_52_WEEK_LOW"
    assert NotificationType.TARGET_PRICE_REACHED.value == "TARGET_PRICE_REACHED"

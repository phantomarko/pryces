from decimal import Decimal

from pryces.domain.stocks import MarketState, Stock, StockSnapshot


class TestStockCreation:
    def test_stock_creation_with_required_fields(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

        assert stock.symbol == "AAPL"
        assert stock.current_price == Decimal("150.00")

    def test_stock_creation_with_all_fields(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            name="Apple Inc.",
            currency="USD",
            previous_close_price=Decimal("149.50"),
            open_price=Decimal("149.75"),
            day_high=Decimal("151.00"),
            day_low=Decimal("149.00"),
            fifty_day_average=Decimal("145.00"),
            two_hundred_day_average=Decimal("140.00"),
            fifty_two_week_high=Decimal("160.00"),
            fifty_two_week_low=Decimal("120.00"),
        )

        assert stock.symbol == "AAPL"
        assert stock.current_price == Decimal("150.00")
        assert stock.name == "Apple Inc."
        assert stock.currency == "USD"
        assert stock.previous_close_price == Decimal("149.50")
        assert stock.open_price == Decimal("149.75")
        assert stock.day_high == Decimal("151.00")
        assert stock.day_low == Decimal("149.00")
        assert stock.fifty_day_average == Decimal("145.00")
        assert stock.two_hundred_day_average == Decimal("140.00")
        assert stock.fifty_two_week_high == Decimal("160.00")
        assert stock.fifty_two_week_low == Decimal("120.00")

    def test_stock_is_immutable(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

        try:
            stock.symbol = "GOOGL"
            assert False, "Should not be able to modify frozen dataclass"
        except AttributeError:
            pass

    def test_stock_optional_fields_default_to_none(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

        assert stock.name is None
        assert stock.currency is None
        assert stock.previous_close_price is None
        assert stock.open_price is None
        assert stock.day_high is None
        assert stock.day_low is None
        assert stock.fifty_day_average is None
        assert stock.two_hundred_day_average is None
        assert stock.fifty_two_week_high is None
        assert stock.fifty_two_week_low is None


class TestHasCrossedSMA:
    def test_has_crossed_sma_returns_false_when_fields_are_missing(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
        stock.generate_notifications()
        messages = stock.drain_notifications()
        assert not any("crossed SMA50" in m for m in messages)

        stock_with_previous = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("140.00"),
            market_state=MarketState.OPEN,
        )
        stock_with_previous.generate_notifications()
        messages = stock_with_previous.drain_notifications()
        assert not any("crossed SMA50" in m for m in messages)

        stock_with_average = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock_with_average.generate_notifications()
        messages = stock_with_average.drain_notifications()
        assert not any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_above(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("140.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_below(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("140.00"),
            previous_close_price=Decimal("150.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_returns_false_when_no_crossing(self):
        stock_both_above = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("148.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock_both_above.generate_notifications()
        messages = stock_both_above.drain_notifications()
        assert not any("crossed SMA50" in m for m in messages)

        stock_both_below = Stock(
            symbol="AAPL",
            current_price=Decimal("140.00"),
            previous_close_price=Decimal("142.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock_both_below.generate_notifications()
        messages = stock_both_below.drain_notifications()
        assert not any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_above_when_current_equals_average(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("145.00"),
            previous_close_price=Decimal("140.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_detects_crossing_below_when_current_equals_average(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("145.00"),
            previous_close_price=Decimal("150.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("crossed SMA50" in m for m in messages)

    def test_has_crossed_sma_returns_false_when_previous_equals_average(self):
        stock_current_above = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("145.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock_current_above.generate_notifications()
        messages = stock_current_above.drain_notifications()
        assert not any("crossed SMA50" in m for m in messages)

        stock_current_below = Stock(
            symbol="AAPL",
            current_price=Decimal("140.00"),
            previous_close_price=Decimal("145.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock_current_below.generate_notifications()
        messages = stock_current_below.drain_notifications()
        assert not any("crossed SMA50" in m for m in messages)


class TestIsCloseToSMA:
    def test_is_close_to_sma_returns_false_when_fields_are_missing(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
        stock.generate_notifications()
        messages = stock.drain_notifications()
        assert not any("SMA50 at" in m for m in messages)

        stock_with_previous = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("140.00"),
            market_state=MarketState.OPEN,
        )
        stock_with_previous.generate_notifications()
        messages = stock_with_previous.drain_notifications()
        assert not any("SMA50 at" in m for m in messages)

        stock_with_average = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock_with_average.generate_notifications()
        messages = stock_with_average.drain_notifications()
        assert not any("SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_true_when_approaching_from_below_within_threshold(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("95.00"),
            fifty_day_average=Decimal("105.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("below SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_true_when_approaching_from_above_within_threshold(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("105.00"),
            fifty_day_average=Decimal("95.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("above SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_false_when_approaching_from_below_beyond_threshold(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("95.00"),
            fifty_day_average=Decimal("106.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_false_when_approaching_from_above_beyond_threshold(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("105.00"),
            fifty_day_average=Decimal("94.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_true_at_exact_threshold_from_below(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("95.00"),
            fifty_day_average=Decimal("105.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("below SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_true_at_exact_threshold_from_above(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("105.00"),
            fifty_day_average=Decimal("95.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("above SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_false_when_previous_close_on_same_side_as_price(self):
        stock_both_above = Stock(
            symbol="AAPL",
            current_price=Decimal("110.00"),
            previous_close_price=Decimal("108.00"),
            fifty_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock_both_above.generate_notifications()
        messages = stock_both_above.drain_notifications()
        assert not any("SMA50 at" in m for m in messages)

        stock_both_below = Stock(
            symbol="AAPL",
            current_price=Decimal("90.00"),
            previous_close_price=Decimal("92.00"),
            fifty_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock_both_below.generate_notifications()
        messages = stock_both_below.drain_notifications()
        assert not any("SMA50 at" in m for m in messages)

    def test_is_close_to_sma_returns_false_when_previous_equals_average(self):
        stock_current_above = Stock(
            symbol="AAPL",
            current_price=Decimal("103.00"),
            previous_close_price=Decimal("100.00"),
            fifty_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock_current_above.generate_notifications()
        messages = stock_current_above.drain_notifications()
        assert not any("SMA50 at" in m for m in messages)

        stock_current_below = Stock(
            symbol="AAPL",
            current_price=Decimal("97.00"),
            previous_close_price=Decimal("100.00"),
            fifty_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock_current_below.generate_notifications()
        messages = stock_current_below.drain_notifications()
        assert not any("SMA50 at" in m for m in messages)


class TestCloseToSMA50Notifications:
    def test_generate_notifications_adds_close_to_sma50_when_approaching_from_below(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("95.00"),
            fifty_day_average=Decimal("103.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("below SMA50 at" in m for m in messages)

    def test_generate_notifications_adds_close_to_sma50_when_approaching_from_above(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("105.00"),
            fifty_day_average=Decimal("97.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("above SMA50 at" in m for m in messages)

    def test_generate_notifications_does_not_add_close_to_sma50_when_beyond_threshold(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("95.00"),
            fifty_day_average=Decimal("110.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("SMA50 at" in m for m in messages)

    def test_generate_notifications_does_not_add_close_to_sma50_when_previous_close_on_same_side(
        self,
    ):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("110.00"),
            previous_close_price=Decimal("108.00"),
            fifty_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("SMA50 at" in m for m in messages)


class TestCloseToSMA200Notifications:
    def test_generate_notifications_adds_close_to_sma200_when_approaching_from_below(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("95.00"),
            two_hundred_day_average=Decimal("103.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("below SMA200 at" in m for m in messages)

    def test_generate_notifications_adds_close_to_sma200_when_approaching_from_above(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("105.00"),
            two_hundred_day_average=Decimal("97.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("above SMA200 at" in m for m in messages)

    def test_generate_notifications_does_not_add_close_to_sma200_when_beyond_threshold(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("95.00"),
            two_hundred_day_average=Decimal("110.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("SMA200 at" in m for m in messages)

    def test_generate_notifications_does_not_add_close_to_sma200_when_previous_close_on_same_side(
        self,
    ):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("110.00"),
            previous_close_price=Decimal("108.00"),
            two_hundred_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("SMA200 at" in m for m in messages)


class TestPercentageFromPreviousClose:
    def test_generate_notifications_rises_when_positive_percentage(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("rose to" in m for m in messages)

    def test_generate_notifications_drops_when_negative_percentage(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("90.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("dropped to" in m for m in messages)

    def test_generate_notifications_no_percentage_when_prices_are_equal(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("rose to" in m for m in messages)
        assert not any("dropped to" in m for m in messages)


class TestSMACrossingNotifications:
    def test_generate_notifications_adds_fifty_day_notification(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("140.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 2
        assert any("crossed SMA50" in m for m in messages)
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_adds_two_hundred_day_notification(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("130.00"),
            two_hundred_day_average=Decimal("140.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 2
        assert any("crossed SMA200" in m for m in messages)
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_adds_both_notifications(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("130.00"),
            fifty_day_average=Decimal("145.00"),
            two_hundred_day_average=Decimal("140.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 3
        assert any("crossed SMA50" in m for m in messages)
        assert any("crossed SMA200" in m for m in messages)
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_adds_no_notifications_when_no_crossing(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("148.00"),
            fifty_day_average=Decimal("120.00"),
            two_hundred_day_average=Decimal("110.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("opened at" in m for m in messages)
        assert not any("crossed SMA50" in m for m in messages)
        assert not any("crossed SMA200" in m for m in messages)


class TestRegularMarketOpenNotifications:
    def test_generate_notifications_adds_regular_market_open_notification(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            open_price=Decimal("149.75"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_generate_notifications_adds_regular_market_open_with_current_price_fallback(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_generate_notifications_does_not_add_regular_market_open_when_market_closed(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            open_price=Decimal("149.75"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.CLOSED,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert messages == []

    def test_generate_notifications_returns_empty_when_market_state_is_none(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert messages == []


class TestMarketOpenDeferral:
    def test_first_call_returns_only_market_open_notification(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("106.00"),
            previous_close_price=Decimal("100.00"),
            fifty_day_average=Decimal("103.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert "opened at" in messages[0]

    def test_second_call_returns_deferred_notifications(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("140.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 2
        assert any("crossed SMA50" in m for m in messages)
        assert any("rose to" in m for m in messages)

    def test_non_first_open_generates_all_notifications_together(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("140.00"),
            fifty_day_average=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("crossed SMA50" in m for m in messages)
        assert any("rose to" in m for m in messages)


class TestMarketStatePost:
    def test_generate_notifications_does_not_add_market_closed_for_non_post_states(self):
        for state in [MarketState.OPEN, MarketState.PRE, MarketState.CLOSED]:
            stock = Stock(
                symbol="AAPL",
                current_price=Decimal("150.00"),
                market_state=state,
            )
            stock.generate_notifications()
            messages = stock.drain_notifications()
            assert not any("closed at" in m for m in messages)

    def test_generate_notifications_returns_empty_when_market_state_is_none(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert messages == []


class TestRegularMarketClosedNotifications:
    def test_generate_notifications_adds_regular_market_closed_when_post(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.POST,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("closed at" in m for m in messages)


class TestPercentageChangeNotifications:
    def test_generate_notifications_adds_twenty_percent_increase(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("121.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_adds_fifteen_percent_increase(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("116.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_adds_ten_percent_increase(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("111.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_adds_five_percent_increase(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("106.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_adds_twenty_percent_decrease(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("79.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("dropped to" in m for m in messages)

    def test_generate_notifications_adds_fifteen_percent_decrease(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("84.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("dropped to" in m for m in messages)

    def test_generate_notifications_adds_ten_percent_decrease(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("89.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("dropped to" in m for m in messages)

    def test_generate_notifications_adds_five_percent_decrease(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("94.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("dropped to" in m for m in messages)

    def test_generate_notifications_no_percentage_below_threshold(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("104.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("opened at" in m for m in messages)

    def test_generate_notifications_percentage_at_exact_threshold(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("105.00"),
            previous_close_price=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("rose to" in m for m in messages)

    def test_generate_notifications_no_percentage_when_previous_close_none(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            market_state=MarketState.OPEN,
        )

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert len(messages) == 1
        assert any("opened at" in m for m in messages)


class Test52WeekHighNotifications:
    def test_generate_new_52_week_high_notification_does_not_add_when_no_snapshot(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("200.00"), market_state=MarketState.OPEN)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("52-week high" in m for m in messages)

    def test_generate_new_52_week_high_notification_does_not_add_when_snapshot_has_no_52_week_high(
        self,
    ):
        stock = Stock(symbol="AAPL", current_price=Decimal("180.00"), market_state=MarketState.OPEN)
        source = Stock(
            symbol="AAPL", current_price=Decimal("200.00"), market_state=MarketState.OPEN
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("52-week high" in m for m in messages)

    def test_generate_new_52_week_high_notification_does_not_add_when_current_price_equals_snapshot_52_week_high(
        self,
    ):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("170.00"),
            fifty_two_week_high=Decimal("180.00"),
            market_state=MarketState.OPEN,
        )
        source = Stock(
            symbol="AAPL", current_price=Decimal("180.00"), market_state=MarketState.OPEN
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("52-week high" in m for m in messages)

    def test_generate_new_52_week_high_notification_does_not_add_when_current_price_below_snapshot_52_week_high(
        self,
    ):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("160.00"),
            fifty_two_week_high=Decimal("180.00"),
            market_state=MarketState.OPEN,
        )
        source = Stock(
            symbol="AAPL", current_price=Decimal("170.00"), market_state=MarketState.OPEN
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("52-week high" in m for m in messages)

    def test_generate_new_52_week_high_notification_adds_when_current_price_exceeds_snapshot_52_week_high(
        self,
    ):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("170.00"),
            fifty_two_week_high=Decimal("180.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        source = Stock(
            symbol="AAPL", current_price=Decimal("200.00"), market_state=MarketState.OPEN
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("52-week high" in m for m in messages)


class Test52WeekLowNotifications:
    def test_generate_new_52_week_low_notification_does_not_add_when_no_snapshot(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("100.00"), market_state=MarketState.OPEN)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("52-week low" in m for m in messages)

    def test_generate_new_52_week_low_notification_does_not_add_when_snapshot_has_no_52_week_low(
        self,
    ):
        stock = Stock(symbol="AAPL", current_price=Decimal("120.00"), market_state=MarketState.OPEN)
        source = Stock(
            symbol="AAPL", current_price=Decimal("100.00"), market_state=MarketState.OPEN
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("52-week low" in m for m in messages)

    def test_generate_new_52_week_low_notification_does_not_add_when_current_price_equals_snapshot_52_week_low(
        self,
    ):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("130.00"),
            fifty_two_week_low=Decimal("120.00"),
            market_state=MarketState.OPEN,
        )
        source = Stock(
            symbol="AAPL", current_price=Decimal("120.00"), market_state=MarketState.OPEN
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("52-week low" in m for m in messages)

    def test_generate_new_52_week_low_notification_does_not_add_when_current_price_above_snapshot_52_week_low(
        self,
    ):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("140.00"),
            fifty_two_week_low=Decimal("120.00"),
            market_state=MarketState.OPEN,
        )
        source = Stock(
            symbol="AAPL", current_price=Decimal("130.00"), market_state=MarketState.OPEN
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("52-week low" in m for m in messages)

    def test_generate_new_52_week_low_notification_adds_when_current_price_falls_below_snapshot_52_week_low(
        self,
    ):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("130.00"),
            fifty_two_week_low=Decimal("120.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        source = Stock(
            symbol="AAPL", current_price=Decimal("100.00"), market_state=MarketState.OPEN
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("52-week low" in m for m in messages)


class TestPriceDelayField:
    def test_stock_price_delay_in_minutes_accepts_int_and_none(self):
        stock_real_time = Stock(
            symbol="AAPL", current_price=Decimal("150.00"), price_delay_in_minutes=0
        )
        assert stock_real_time.price_delay_in_minutes == 0

        stock_delayed = Stock(
            symbol="AAPL", current_price=Decimal("150.00"), price_delay_in_minutes=15
        )
        assert stock_delayed.price_delay_in_minutes == 15

        stock_none = Stock(symbol="AAPL", current_price=Decimal("150.00"))
        assert stock_none.price_delay_in_minutes is None


class TestUpdate:
    def test_snapshot_defaults_to_none(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))

        assert stock.snapshot is None

    def test_update_captures_snapshot_of_previous_state(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            fifty_two_week_high=Decimal("160.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=0,
        )
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("155.00"),
            fifty_two_week_high=Decimal("165.00"),
            market_state=MarketState.OPEN,
        )

        stock.update(source)

        assert stock.snapshot is not None
        assert stock.snapshot.current_price == Decimal("150.00")
        assert stock.snapshot.fifty_two_week_high == Decimal("160.00")
        assert stock.snapshot.market_state == MarketState.OPEN
        assert stock.snapshot.price_delay_in_minutes == 0

    def test_update_copies_fields_from_source(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("155.00"),
            name="Apple Inc.",
            currency="USD",
            previous_close_price=Decimal("149.00"),
            open_price=Decimal("150.00"),
            day_high=Decimal("156.00"),
            day_low=Decimal("148.00"),
            fifty_day_average=Decimal("145.00"),
            two_hundred_day_average=Decimal("140.00"),
            fifty_two_week_high=Decimal("170.00"),
            fifty_two_week_low=Decimal("120.00"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
        )

        stock.update(source)

        assert stock.current_price == Decimal("155.00")
        assert stock.name == "Apple Inc."
        assert stock.currency == "USD"
        assert stock.previous_close_price == Decimal("149.00")
        assert stock.open_price == Decimal("150.00")
        assert stock.day_high == Decimal("156.00")
        assert stock.day_low == Decimal("148.00")
        assert stock.fifty_day_average == Decimal("145.00")
        assert stock.two_hundred_day_average == Decimal("140.00")
        assert stock.fifty_two_week_high == Decimal("170.00")
        assert stock.fifty_two_week_low == Decimal("120.00")
        assert stock.market_state == MarketState.OPEN
        assert stock.price_delay_in_minutes == 15

    def test_update_preserves_symbol(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"))
        source = Stock(symbol="AAPL", current_price=Decimal("155.00"))

        stock.update(source)

        assert stock.symbol == "AAPL"

    def test_update_preserves_notifications(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        result1 = stock.drain_notifications()
        assert len(result1) > 0

        source = Stock(symbol="AAPL", current_price=Decimal("155.00"))
        stock.update(source)

        stock.generate_notifications()
        result2 = stock.drain_notifications()
        assert result2 == []  # dedup works — notifications survived the update

    def test_stock_snapshot_is_frozen(self):
        snapshot = StockSnapshot(
            current_price=Decimal("150.00"),
            previous_close_price=None,
            open_price=None,
            day_high=None,
            day_low=None,
            fifty_day_average=None,
            two_hundred_day_average=None,
            fifty_two_week_high=None,
            fifty_two_week_low=None,
            market_state=None,
            price_delay_in_minutes=None,
        )

        try:
            snapshot.current_price = Decimal("200.00")
            assert False, "Should not be able to modify frozen dataclass"
        except AttributeError:
            pass


class TestMarketStateTransition:
    def test_is_market_state_transition_returns_false_when_no_snapshot(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)

        assert stock.is_market_state_transition() is False

    def test_is_market_state_transition_returns_true_when_pre_to_open(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.PRE)
        source = Stock(
            symbol="AAPL", current_price=Decimal("155.00"), market_state=MarketState.OPEN
        )
        stock.update(source)

        assert stock.is_market_state_transition() is True

    def test_is_market_state_transition_returns_true_when_open_to_post(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
        source = Stock(
            symbol="AAPL", current_price=Decimal("155.00"), market_state=MarketState.POST
        )
        stock.update(source)

        assert stock.is_market_state_transition() is True

    def test_is_market_state_transition_returns_false_when_same_state(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
        source = Stock(
            symbol="AAPL", current_price=Decimal("155.00"), market_state=MarketState.OPEN
        )
        stock.update(source)

        assert stock.is_market_state_transition() is False

    def test_is_market_state_transition_returns_false_when_transition_to_non_open_post(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
        source = Stock(symbol="AAPL", current_price=Decimal("155.00"), market_state=MarketState.PRE)
        stock.update(source)

        assert stock.is_market_state_transition() is False


class TestDeduplication:
    def test_generate_notifications_deduplicates_by_type(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        result1 = stock.drain_notifications()
        assert len(result1) > 0

        stock.generate_notifications()
        result2 = stock.drain_notifications()

        assert result2 == []

    def test_generate_notifications_returns_new_notifications_only(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("101.00"),
            previous_close_price=Decimal("99.00"),
            fifty_day_average=Decimal("100.00"),
            two_hundred_day_average=Decimal("80.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        result1 = stock.drain_notifications()
        assert len(result1) > 0
        stock.generate_notifications()
        result2 = stock.drain_notifications()
        assert len(result2) > 0

        stock.generate_notifications()
        result3 = stock.drain_notifications()

        assert result3 == []


class TestCloseToSMASuppressedByCrossing:
    def test_close_to_sma50_suppressed_when_sma50_was_crossed(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("101.00"),
            previous_close_price=Decimal("99.00"),
            fifty_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        first_messages = stock.drain_notifications()
        assert any("crossed SMA50" in m for m in first_messages)

        source = Stock(
            symbol="AAPL",
            current_price=Decimal("102.00"),
            previous_close_price=Decimal("101.00"),
            fifty_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("SMA50 at" in m for m in messages)

    def test_close_to_sma200_suppressed_when_sma200_was_crossed(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("101.00"),
            previous_close_price=Decimal("99.00"),
            two_hundred_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        first_messages = stock.drain_notifications()
        assert any("crossed SMA200" in m for m in first_messages)

        source = Stock(
            symbol="AAPL",
            current_price=Decimal("102.00"),
            previous_close_price=Decimal("101.00"),
            two_hundred_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("SMA200 at" in m for m in messages)

    def test_close_to_sma50_not_suppressed_when_no_crossing(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("96.00"),
            previous_close_price=Decimal("95.00"),
            fifty_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("below SMA50 at" in m for m in messages)

    def test_close_to_sma200_not_suppressed_when_no_crossing(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("96.00"),
            previous_close_price=Decimal("95.00"),
            two_hundred_day_average=Decimal("100.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("below SMA200 at" in m for m in messages)


class TestTargetPriceNotifications:
    def test_generate_notifications_appends_target_price_reached_when_target_is_reached(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        stock.sync_targets([Decimal("200.00")])
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert any("hit target" in m for m in messages)

    def test_generate_notifications_removes_triggered_targets_from_stock(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        stock.sync_targets([Decimal("200.00")])
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        stock.generate_notifications()
        stock.drain_notifications()

        assert stock.drain_fulfilled_targets() == [Decimal("200.00")]

    def test_generate_notifications_does_not_include_unreached_target(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )
        stock.sync_targets([Decimal("200.00")])
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("hit target" in m for m in messages)
        assert stock.drain_fulfilled_targets() == []

    def test_generate_notifications_target_notification_message_contains_symbol_and_target(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        stock.sync_targets([Decimal("200.00")])
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        target_messages = [m for m in messages if "hit target" in m]
        assert len(target_messages) == 1
        assert "AAPL" in target_messages[0]
        assert "200.00" in target_messages[0]

    def test_generate_notifications_ignores_targets_when_market_is_post(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.POST,
        )
        stock.sync_targets([Decimal("200.00")])
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.POST,
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        assert not any("hit target" in m for m in messages)
        assert stock.drain_fulfilled_targets() == []

    def test_generate_notifications_removes_multiple_triggered_targets(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("295.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        stock.sync_targets([Decimal("200.00"), Decimal("250.00")])
        source = Stock(
            symbol="AAPL",
            current_price=Decimal("300.00"),
            previous_close_price=Decimal("295.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)

        stock.generate_notifications()
        messages = stock.drain_notifications()

        target_messages = [m for m in messages if "hit target" in m]
        assert len(target_messages) == 2
        assert set(stock.drain_fulfilled_targets()) == {Decimal("200.00"), Decimal("250.00")}

    def test_generate_notifications_target_price_reached_is_never_deduplicated(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("100.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        stock.sync_targets([Decimal("200.00")])
        source1 = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source1)
        stock.generate_notifications()
        result1 = stock.drain_notifications()
        assert any("hit target" in m for m in result1)

        stock.sync_targets([Decimal("250.00")])
        source2 = Stock(
            symbol="AAPL",
            current_price=Decimal("250.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source2)
        stock.generate_notifications()
        result2 = stock.drain_notifications()
        assert any("hit target" in m for m in result2)


class TestSyncTargets:
    def test_sync_targets_sets_entry_price(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
        stock.sync_targets([Decimal("200.00")])

        source_below = Stock(
            symbol="AAPL",
            current_price=Decimal("180.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source_below)
        stock.generate_notifications()
        messages_below = stock.drain_notifications()
        assert not any("hit target" in m for m in messages_below)
        assert stock.drain_fulfilled_targets() == []

        source_hit = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            previous_close_price=Decimal("195.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source_hit)
        stock.generate_notifications()
        messages_hit = stock.drain_notifications()
        assert any("hit target" in m for m in messages_hit)

    def test_sync_targets_removes_missing_targets(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
        stock.generate_notifications()
        stock.drain_notifications()
        stock.sync_targets([Decimal("200.00"), Decimal("250.00")])
        stock.sync_targets([Decimal("200.00")])

        source = Stock(
            symbol="AAPL",
            current_price=Decimal("260.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications()
        stock.drain_notifications()

        assert stock.drain_fulfilled_targets() == [Decimal("200.00")]

    def test_sync_targets_clears_all_on_empty_list(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
        stock.sync_targets([Decimal("200.00")])
        stock.sync_targets([])

        source = Stock(
            symbol="AAPL",
            current_price=Decimal("200.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications()
        stock.drain_notifications()

        assert stock.drain_fulfilled_targets() == []

    def test_sync_targets_adds_new_and_preserves_existing(self):
        stock = Stock(symbol="AAPL", current_price=Decimal("150.00"), market_state=MarketState.OPEN)
        stock.generate_notifications()
        stock.drain_notifications()
        stock.sync_targets([Decimal("200.00")])
        stock.sync_targets([Decimal("200.00"), Decimal("250.00")])

        source = Stock(
            symbol="AAPL",
            current_price=Decimal("260.00"),
            previous_close_price=Decimal("148.00"),
            market_state=MarketState.OPEN,
        )
        stock.update(source)
        stock.generate_notifications()
        stock.drain_notifications()

        assert set(stock.drain_fulfilled_targets()) == {Decimal("200.00"), Decimal("250.00")}


class TestDrainFulfilledTargets:
    def test_drain_fulfilled_targets_returns_fulfilled_targets(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock.generate_notifications()
        stock.drain_notifications()
        stock.sync_targets([Decimal("150.00")])
        stock.generate_notifications()
        stock.drain_notifications()

        fulfilled = stock.drain_fulfilled_targets()

        assert len(fulfilled) == 1
        assert fulfilled[0] == Decimal("150.00")

    def test_drain_fulfilled_targets_clears_list_after_drain(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock.sync_targets([Decimal("150.00")])
        stock.generate_notifications()
        stock.drain_notifications()
        stock.drain_fulfilled_targets()

        second_drain = stock.drain_fulfilled_targets()

        assert second_drain == []

    def test_drain_fulfilled_targets_returns_empty_when_no_targets_fulfilled(self):
        stock = Stock(
            symbol="AAPL",
            current_price=Decimal("150.00"),
            previous_close_price=Decimal("145.00"),
            market_state=MarketState.OPEN,
        )
        stock.sync_targets([Decimal("200.00")])
        stock.generate_notifications()
        stock.drain_notifications()

        fulfilled = stock.drain_fulfilled_targets()

        assert fulfilled == []

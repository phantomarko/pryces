from decimal import Decimal

from pryces.infrastructure.formatters import ConsolidatingNotificationFormatter
from pryces.domain.stocks import (
    CapSize,
    Currency,
    InstrumentType,
    MarketState,
    Stock,
    StockSnapshot,
)
from tests.fixtures.factories import (
    _DEFAULT_NOW,
    generate_and_drain,
    make_stock,
)

_formatter = ConsolidatingNotificationFormatter()


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
            currency=Currency.USD,
            previous_close_price=Decimal("149.50"),
            open_price=Decimal("149.75"),
            day_high=Decimal("151.00"),
            day_low=Decimal("149.00"),
            fifty_day_average=Decimal("145.00"),
            two_hundred_day_average=Decimal("140.00"),
            fifty_two_week_high=Decimal("160.00"),
            fifty_two_week_low=Decimal("120.00"),
            kind=InstrumentType.STOCK,
        )

        assert stock.symbol == "AAPL"
        assert stock.current_price == Decimal("150.00")
        assert stock.name == "Apple Inc."
        assert stock.currency == Currency.USD
        assert stock.previous_close_price == Decimal("149.50")
        assert stock.open_price == Decimal("149.75")
        assert stock.day_high == Decimal("151.00")
        assert stock.day_low == Decimal("149.00")
        assert stock.fifty_day_average == Decimal("145.00")
        assert stock.two_hundred_day_average == Decimal("140.00")
        assert stock.fifty_two_week_high == Decimal("160.00")
        assert stock.fifty_two_week_low == Decimal("120.00")
        assert stock.kind == InstrumentType.STOCK

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
            currency=Currency.USD,
            previous_close_price=Decimal("149.00"),
            open_price=Decimal("150.00"),
            day_high=Decimal("156.00"),
            day_low=Decimal("148.00"),
            fifty_day_average=Decimal("145.00"),
            two_hundred_day_average=Decimal("140.00"),
            fifty_two_week_high=Decimal("170.00"),
            fifty_two_week_low=Decimal("120.00"),
            market_cap=Decimal("2500000000000"),
            market_state=MarketState.OPEN,
            price_delay_in_minutes=15,
        )

        stock.update(source)

        assert stock.current_price == Decimal("155.00")
        assert stock.name == "Apple Inc."
        assert stock.currency == Currency.USD
        assert stock.previous_close_price == Decimal("149.00")
        assert stock.open_price == Decimal("150.00")
        assert stock.day_high == Decimal("156.00")
        assert stock.day_low == Decimal("148.00")
        assert stock.fifty_day_average == Decimal("145.00")
        assert stock.two_hundred_day_average == Decimal("140.00")
        assert stock.fifty_two_week_high == Decimal("170.00")
        assert stock.fifty_two_week_low == Decimal("120.00")
        assert stock.market_cap == Decimal("2500000000000")
        assert stock.market_state == MarketState.OPEN
        assert stock.price_delay_in_minutes == 15

    def test_update_preserves_symbol(self):
        stock = make_stock(current_price="150.00")
        source = make_stock(current_price="155.00")
        stock.update(source)
        assert stock.symbol == "AAPL"

    def test_update_preserves_notifications(self):
        stock = make_stock(current_price="150.00", previous_close_price="148.00")
        result1 = generate_and_drain(stock)
        assert len(result1) > 0

        source = make_stock(current_price="155.00")
        stock.update(source)

        result2 = generate_and_drain(stock)
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
        stock = make_stock(current_price="150.00")
        assert stock.is_market_state_transition() is False

    def test_is_market_state_transition_returns_true_when_pre_to_open(self):
        stock = make_stock(current_price="150.00", market_state=MarketState.PRE)
        source = make_stock(current_price="155.00", market_state=MarketState.OPEN)
        stock.update(source)
        assert stock.is_market_state_transition() is True

    def test_is_market_state_transition_returns_true_when_open_to_post(self):
        stock = make_stock(current_price="150.00", market_state=MarketState.OPEN)
        source = make_stock(current_price="155.00", market_state=MarketState.POST)
        stock.update(source)
        assert stock.is_market_state_transition() is True

    def test_is_market_state_transition_returns_false_when_same_state(self):
        stock = make_stock(current_price="150.00", market_state=MarketState.OPEN)
        source = make_stock(current_price="155.00", market_state=MarketState.OPEN)
        stock.update(source)
        assert stock.is_market_state_transition() is False

    def test_is_market_state_transition_returns_false_when_transition_to_non_open_post(self):
        stock = make_stock(current_price="150.00", market_state=MarketState.OPEN)
        source = make_stock(current_price="155.00", market_state=MarketState.PRE)
        stock.update(source)
        assert stock.is_market_state_transition() is False


class TestCapSize:
    def test_large_cap(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.USD, market_cap="10000000000"
        )
        assert stock.cap_size == CapSize.LARGE

    def test_large_cap_above_threshold(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.USD, market_cap="500000000000"
        )
        assert stock.cap_size == CapSize.LARGE

    def test_mid_cap(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.USD, market_cap="2000000000"
        )
        assert stock.cap_size == CapSize.MID

    def test_mid_cap_between_thresholds(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.USD, market_cap="5000000000"
        )
        assert stock.cap_size == CapSize.MID

    def test_mid_cap_just_below_large(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.USD, market_cap="9999999999"
        )
        assert stock.cap_size == CapSize.MID

    def test_small_cap(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.USD, market_cap="1999999999"
        )
        assert stock.cap_size == CapSize.SMALL

    def test_small_cap_low_value(self):
        stock = make_stock(kind=InstrumentType.STOCK, currency=Currency.USD, market_cap="100000000")
        assert stock.cap_size == CapSize.SMALL

    def test_none_when_kind_is_etf(self):
        stock = make_stock(kind=InstrumentType.ETF, currency=Currency.USD, market_cap="50000000000")
        assert stock.cap_size is None

    def test_none_when_kind_is_crypto(self):
        stock = make_stock(
            kind=InstrumentType.CRYPTO, currency=Currency.USD, market_cap="50000000000"
        )
        assert stock.cap_size is None

    def test_none_when_kind_is_index(self):
        stock = make_stock(
            kind=InstrumentType.INDEX, currency=Currency.USD, market_cap="50000000000"
        )
        assert stock.cap_size is None

    def test_none_when_kind_is_none(self):
        stock = make_stock(currency=Currency.USD, market_cap="50000000000")
        assert stock.cap_size is None

    def test_large_cap_eur(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.EUR, market_cap="10000000000"
        )
        assert stock.cap_size == CapSize.LARGE

    def test_mid_cap_eur(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.EUR, market_cap="5000000000"
        )
        assert stock.cap_size == CapSize.MID

    def test_small_cap_eur(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.EUR, market_cap="1999999999"
        )
        assert stock.cap_size == CapSize.SMALL

    def test_none_when_currency_is_unsupported(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.GBP, market_cap="50000000000"
        )
        assert stock.cap_size is None

    def test_none_when_currency_is_none(self):
        stock = make_stock(kind=InstrumentType.STOCK, market_cap="50000000000")
        assert stock.cap_size is None

    def test_none_when_market_cap_is_none(self):
        stock = make_stock(kind=InstrumentType.STOCK, currency=Currency.USD)
        assert stock.cap_size is None

    def test_recomputed_after_update(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.USD, market_cap="1000000000"
        )
        assert stock.cap_size == CapSize.SMALL

        updated = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.USD, market_cap="15000000000"
        )
        stock.update(updated)
        assert stock.cap_size == CapSize.LARGE

    def test_recomputed_to_none_after_update_changes_kind(self):
        stock = make_stock(
            kind=InstrumentType.STOCK, currency=Currency.USD, market_cap="15000000000"
        )
        assert stock.cap_size == CapSize.LARGE

        updated = make_stock(
            kind=InstrumentType.ETF, currency=Currency.USD, market_cap="15000000000"
        )
        stock.update(updated)
        assert stock.cap_size is None

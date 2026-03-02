from decimal import Decimal

from pryces.domain.stocks import MarketState
from pryces.infrastructure.providers import YahooFinanceMapper


def _build_full_info(**overrides) -> dict:
    info = {
        "currentPrice": 150.25,
        "regularMarketPrice": 150.25,
        "previousClose": 148.50,
        "open": 149.00,
        "dayHigh": 151.00,
        "dayLow": 148.00,
        "fiftyDayAverage": 145.00,
        "twoHundredDayAverage": 140.00,
        "fiftyTwoWeekHigh": 160.00,
        "fiftyTwoWeekLow": 120.00,
        "longName": "Test Company Inc.",
        "shortName": "Test Co",
        "currency": "USD",
        "marketState": "REGULAR",
        "exchangeDataDelayedBy": 0,
    }
    info.update(overrides)
    return info


class TestYahooFinanceMapper:
    def test_maps_full_info_to_stock(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)

        stock = mapper.map("AAPL", _build_full_info())

        assert stock is not None
        assert stock.symbol == "AAPL"
        assert stock.current_price == Decimal("150.25")
        assert stock.name == "Test Company Inc."
        assert stock.currency == "USD"
        assert stock.previous_close_price == Decimal("148.5")
        assert stock.open_price == Decimal("149.0")
        assert stock.day_high == Decimal("151.0")
        assert stock.day_low == Decimal("148.0")
        assert stock.fifty_day_average == Decimal("145.0")
        assert stock.two_hundred_day_average == Decimal("140.0")
        assert stock.fifty_two_week_high == Decimal("160.0")
        assert stock.fifty_two_week_low == Decimal("120.0")
        assert stock.market_state == MarketState.OPEN
        assert stock.price_delay_in_minutes == 0

    def test_returns_none_for_empty_info(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)

        assert mapper.map("AAPL", {}) is None

    def test_returns_none_for_small_metadata_dict(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)
        info = {"key1": "val1", "key2": "val2", "key3": "val3"}

        assert mapper.map("AAPL", info) is None

    def test_returns_none_when_no_price_available(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)
        info = _build_full_info()
        del info["currentPrice"]
        del info["regularMarketPrice"]
        del info["previousClose"]

        assert mapper.map("AAPL", info) is None

    def test_price_fallback_to_regular_market_price(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)
        info = _build_full_info()
        del info["currentPrice"]
        info["regularMarketPrice"] = 155.00

        stock = mapper.map("AAPL", info)

        assert stock is not None
        assert stock.current_price == Decimal("155.0")

    def test_price_fallback_to_previous_close(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)
        info = _build_full_info()
        del info["currentPrice"]
        del info["regularMarketPrice"]
        info["previousClose"] = 148.50

        stock = mapper.map("AAPL", info)

        assert stock is not None
        assert stock.current_price == Decimal("148.5")

    def test_maps_market_states(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)
        cases = {
            "REGULAR": MarketState.OPEN,
            "PRE": MarketState.PRE,
            "PREPRE": MarketState.PRE,
            "POST": MarketState.POST,
            "POSTPOST": MarketState.POST,
            "CLOSED": MarketState.CLOSED,
        }
        for yfinance_value, expected_state in cases.items():
            info = _build_full_info(marketState=yfinance_value)

            stock = mapper.map("AAPL", info)

            assert stock is not None
            assert (
                stock.market_state == expected_state
            ), f"Expected {expected_state} for '{yfinance_value}'"

    def test_maps_unknown_market_state_to_none(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)
        info = _build_full_info(marketState="UNKNOWN_STATE")

        stock = mapper.map("AAPL", info)

        assert stock is not None
        assert stock.market_state is None

    def test_maps_none_market_state_to_none(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)
        info = _build_full_info(marketState=None)

        stock = mapper.map("AAPL", info)

        assert stock is not None
        assert stock.market_state is None

    def test_adds_extra_delay_when_delay_positive(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=5)
        info = _build_full_info(exchangeDataDelayedBy=15)

        stock = mapper.map("AAPL", info)

        assert stock is not None
        assert stock.price_delay_in_minutes == 20

    def test_uses_extra_delay_when_exchange_delay_zero(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=5)
        info = _build_full_info(exchangeDataDelayedBy=0)

        stock = mapper.map("AAPL", info)

        assert stock is not None
        assert stock.price_delay_in_minutes == 5

    def test_uses_extra_delay_when_exchange_delay_null(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=5)
        info = _build_full_info(exchangeDataDelayedBy=None)

        stock = mapper.map("AAPL", info)

        assert stock is not None
        assert stock.price_delay_in_minutes == 5

    def test_handles_missing_optional_fields(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)
        info = {"currentPrice": 100.0, "k1": "v1", "k2": "v2", "k3": "v3"}

        stock = mapper.map("AAPL", info)

        assert stock is not None
        assert stock.current_price == Decimal("100.0")
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
        assert stock.market_state is None
        assert stock.price_delay_in_minutes == 0

    def test_uppercases_symbol(self):
        mapper = YahooFinanceMapper(extra_delay_in_minutes=0)
        info = _build_full_info()

        stock = mapper.map("aapl", info)

        assert stock is not None
        assert stock.symbol == "AAPL"

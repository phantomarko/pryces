import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from decimal import Decimal

import yfinance as yf

from ..application.interfaces import StockProvider
from ..domain.stocks import MarketState, Stock


@dataclass(frozen=True, slots=True)
class YahooFinanceSettings:
    max_workers: int
    extra_delay_in_minutes: int


class YahooFinanceMapper:
    def __init__(self, extra_delay_in_minutes: int) -> None:
        self._extra_delay_in_minutes = extra_delay_in_minutes
        self._logger = logging.getLogger(__name__)

    def map(self, symbol: str, info: dict) -> Stock | None:
        # yfinance returns a small metadata-only dict (≤3 keys) for invalid/delisted symbols
        if not info or len(info) <= 3:
            self._logger.error(f"No data available for symbol: {symbol}")
            return None

        current_price = None
        for price_key in ["currentPrice", "regularMarketPrice", "previousClose"]:
            if price_key in info and info[price_key] is not None:
                current_price = info[price_key]
                break

        if current_price is None:
            self._logger.error(f"Unable to retrieve current price for symbol: {symbol}")
            return None

        return self._to_stock(symbol, info, current_price)

    def _to_stock(self, symbol: str, info: dict, current_price: float) -> Stock:
        previous_close = info.get("previousClose")
        open_price = info.get("open")
        day_high = info.get("dayHigh")
        day_low = info.get("dayLow")
        fifty_day_avg = info.get("fiftyDayAverage")
        two_hundred_day_avg = info.get("twoHundredDayAverage")
        fifty_two_week_high = info.get("fiftyTwoWeekHigh")
        fifty_two_week_low = info.get("fiftyTwoWeekLow")
        company_name = info.get("longName") or info.get("shortName")
        currency = info.get("currency")
        market_state = self._map_market_state(info.get("marketState"))
        exchange_delay = info.get("exchangeDataDelayedBy") or 0
        price_delay_in_minutes = exchange_delay + self._extra_delay_in_minutes

        return Stock(
            symbol=symbol.upper(),
            current_price=Decimal(str(current_price)),
            name=company_name,
            currency=currency,
            previous_close_price=(
                Decimal(str(previous_close)) if previous_close is not None else None
            ),
            open_price=Decimal(str(open_price)) if open_price is not None else None,
            day_high=Decimal(str(day_high)) if day_high is not None else None,
            day_low=Decimal(str(day_low)) if day_low is not None else None,
            fifty_day_average=Decimal(str(fifty_day_avg)) if fifty_day_avg is not None else None,
            two_hundred_day_average=(
                Decimal(str(two_hundred_day_avg)) if two_hundred_day_avg is not None else None
            ),
            fifty_two_week_high=(
                Decimal(str(fifty_two_week_high)) if fifty_two_week_high is not None else None
            ),
            fifty_two_week_low=(
                Decimal(str(fifty_two_week_low)) if fifty_two_week_low is not None else None
            ),
            market_state=market_state,
            price_delay_in_minutes=price_delay_in_minutes,
        )

    def _map_market_state(self, value: str | None) -> MarketState | None:
        match value:
            case "REGULAR":
                return MarketState.OPEN
            case "PRE" | "PREPRE":
                return MarketState.PRE
            case "POST" | "POSTPOST":
                return MarketState.POST
            case "CLOSED":
                return MarketState.CLOSED
            case None:
                return None
            case _:
                self._logger.warning(f"Unknown market state: {value}")
                return None


class YahooFinanceProvider(StockProvider):
    def __init__(self, settings: YahooFinanceSettings) -> None:
        self._max_workers = settings.max_workers
        self._mapper = YahooFinanceMapper(settings.extra_delay_in_minutes)
        self._logger = logging.getLogger(__name__)

    def get_stock(self, symbol: str) -> Stock | None:
        self._logger.debug(f"Fetching stock data for {symbol}")
        ticker_obj = yf.Ticker(symbol)
        info = ticker_obj.info
        stock = self._mapper.map(symbol, info)
        del info, ticker_obj
        return stock

    def _fetch_stock(self, symbol: str) -> Stock | None:
        try:
            return self.get_stock(symbol)
        except Exception as e:
            self._logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def get_stocks(self, symbols: list[str]) -> list[Stock]:
        if not symbols:
            return []

        with ThreadPoolExecutor(max_workers=min(len(symbols), self._max_workers)) as executor:
            results = list(executor.map(self._fetch_stock, symbols))

        return [stock for stock in results if stock is not None]

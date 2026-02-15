import json
import logging
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from decimal import Decimal

import yfinance as yf

from ..application.interfaces import StockProvider, MessageSender
from ..domain.stocks import MarketState, Stock


@dataclass(frozen=True, slots=True)
class TelegramSettings:
    bot_token: str
    group_id: str


class YahooFinanceProvider(StockProvider):
    def __init__(self, max_workers: int) -> None:
        self._max_workers = max_workers
        self._logger = logging.getLogger(__name__)

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

    def _build_response(self, symbol: str, info: dict, current_price: float) -> Stock:
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

        return Stock(
            symbol=symbol.upper(),
            currentPrice=Decimal(str(current_price)),
            name=company_name,
            currency=currency,
            previousClosePrice=Decimal(str(previous_close)) if previous_close is not None else None,
            openPrice=Decimal(str(open_price)) if open_price is not None else None,
            dayHigh=Decimal(str(day_high)) if day_high is not None else None,
            dayLow=Decimal(str(day_low)) if day_low is not None else None,
            fiftyDayAverage=Decimal(str(fifty_day_avg)) if fifty_day_avg is not None else None,
            twoHundredDayAverage=(
                Decimal(str(two_hundred_day_avg)) if two_hundred_day_avg is not None else None
            ),
            fiftyTwoWeekHigh=(
                Decimal(str(fifty_two_week_high)) if fifty_two_week_high is not None else None
            ),
            fiftyTwoWeekLow=(
                Decimal(str(fifty_two_week_low)) if fifty_two_week_low is not None else None
            ),
            marketState=market_state,
        )

    def _build_stock_from_ticker(self, symbol: str, info: dict) -> Stock | None:
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

        return self._build_response(symbol, info, current_price)

    def get_stock(self, symbol: str) -> Stock | None:
        ticker_obj = yf.Ticker(symbol)
        info = ticker_obj.info
        stock = self._build_stock_from_ticker(symbol, info)
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


class TelegramMessageSender(MessageSender):
    _HEADERS = {"Content-Type": "application/json"}

    def __init__(self, settings: TelegramSettings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)
        self._url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"

    def send_message(self, message: str) -> bool:
        payload = json.dumps({"chat_id": self._settings.group_id, "text": message}).encode("utf-8")

        self._logger.info(f"Sending message to Telegram group {self._settings.group_id}")

        request = urllib.request.Request(self._url, data=payload, headers=self._HEADERS)

        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            self._logger.error(f"Telegram API HTTP {e.code}: {error_body}")
            raise

        response_data = json.loads(response.read().decode("utf-8"))

        if response_data.get("ok") is True:
            self._logger.info(f"Notification sent:\n{message}")
            return True

        self._logger.error(f"Telegram API returned ok=false: {response_data}")
        return False

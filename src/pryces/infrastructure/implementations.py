import json
import logging
import urllib.request
from dataclasses import dataclass
from decimal import Decimal

import yfinance as yf

from ..application.exceptions import StockInformationIncomplete
from ..application.interfaces import StockPriceProvider, StockPrice, MessageSender


@dataclass(frozen=True)
class TelegramSettings:
    bot_token: str
    group_id: str


class YahooFinanceProvider(StockPriceProvider):
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def _build_response(self, symbol: str, info: dict, current_price: float) -> StockPrice:
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

        return StockPrice(
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
        )

    def get_stock_price(self, symbol: str) -> StockPrice | None:
        try:
            self._logger.debug(f"Fetching data for symbol: {symbol}")

            ticker_obj = yf.Ticker(symbol)
            info = ticker_obj.info

            if not info or len(info) <= 3:  # Yahoo Finance returns ≤3 fields for invalid symbols
                self._logger.warning(f"No data available for symbol: {symbol}")
                return None

            current_price = None
            for price_key in ["currentPrice", "regularMarketPrice", "previousClose"]:
                if price_key in info and info[price_key] is not None:
                    current_price = info[price_key]
                    break

            if current_price is None:
                self._logger.error(f"No current price available for symbol: {symbol}")
                raise StockInformationIncomplete(symbol)

            return self._build_response(symbol, info, current_price)

        except Exception as e:
            self._logger.error(f"Error fetching data for {symbol}: {e}")
            raise

    def get_stocks_prices(self, symbols: list[str]) -> list[StockPrice]:
        if not symbols:
            return []

        try:
            self._logger.debug(f"Fetching batch data for symbols: {symbols}")

            # Use yfinance Tickers API for batch fetching
            tickers = yf.Tickers(" ".join(symbols))
            responses = []

            for symbol in symbols:
                try:
                    # Access individual ticker info from batch
                    ticker_obj = tickers.tickers[symbol]
                    info = ticker_obj.info

                    # Check if we got valid data
                    if not info or len(info) <= 3:
                        self._logger.warning(f"No data available for symbol: {symbol}")
                        continue

                    # Extract current price with fallback strategies
                    current_price = None
                    for price_key in ["currentPrice", "regularMarketPrice", "previousClose"]:
                        if price_key in info and info[price_key] is not None:
                            current_price = info[price_key]
                            break

                    if current_price is None:
                        self._logger.warning(f"No current price available for symbol: {symbol}")
                        continue

                    # Build and append response
                    responses.append(self._build_response(symbol, info, current_price))

                except Exception as e:
                    self._logger.warning(f"Error fetching data for {symbol}: {e}")
                    continue

            return responses

        except Exception as e:
            self._logger.error(f"Error in batch fetch: {e}")
            raise


class TelegramMessageSender(MessageSender):
    def __init__(self, settings: TelegramSettings) -> None:
        self._settings = settings
        self._logger = logging.getLogger(__name__)

    def send_message(self, message: str) -> bool:
        url = f"https://api.telegram.org/bot{self._settings.bot_token}/sendMessage"
        payload = json.dumps({"chat_id": self._settings.group_id, "text": message}).encode("utf-8")

        self._logger.debug(f"Sending message to Telegram group {self._settings.group_id}")

        request = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}
        )
        response = urllib.request.urlopen(request)

        response_data = json.loads(response.read().decode("utf-8"))

        if response_data.get("ok") is True:
            self._logger.info("Message sent successfully via Telegram")
            return True

        self._logger.warning(f"Telegram API returned ok=false: {response_data}")
        return False

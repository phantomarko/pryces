"""Stock price provider implementations."""

import logging
from decimal import Decimal

import yfinance as yf

from ..application.exceptions import StockInformationIncomplete
from ..application.providers import StockPriceProvider, StockPriceResponse


class YahooFinanceProvider(StockPriceProvider):
    """Stock price provider using Yahoo Finance API via yfinance library.

    This provider wraps the yfinance library to fetch real-time stock prices
    from Yahoo Finance. It handles price extraction with fallback strategies
    and converts data to match the StockPriceProvider interface.
    """

    def __init__(self) -> None:
        """Initialize the provider."""
        self._logger = logging.getLogger(__name__)

    def _build_response(self, symbol: str, info: dict, current_price: float) -> StockPriceResponse:
        """Build StockPriceResponse from ticker info and price data.

        Args:
            symbol: Stock ticker symbol
            info: Ticker information dictionary from yfinance
            current_price: Current price value (already validated as non-None)

        Returns:
            StockPriceResponse with all available fields
        """
        previous_close = info.get('previousClose')
        open_price = info.get('open')
        day_high = info.get('dayHigh')
        day_low = info.get('dayLow')
        fifty_day_avg = info.get('fiftyDayAverage')
        two_hundred_day_avg = info.get('twoHundredDayAverage')
        fifty_two_week_high = info.get('fiftyTwoWeekHigh')
        fifty_two_week_low = info.get('fiftyTwoWeekLow')

        # Extract optional metadata
        company_name = info.get('longName') or info.get('shortName')
        currency = info.get('currency')

        # Convert all non-None prices to Decimal for precision
        return StockPriceResponse(
            symbol=symbol.upper(),
            currentPrice=Decimal(str(current_price)),
            name=company_name,
            currency=currency,
            previousClosePrice=Decimal(str(previous_close)) if previous_close is not None else None,
            openPrice=Decimal(str(open_price)) if open_price is not None else None,
            dayHigh=Decimal(str(day_high)) if day_high is not None else None,
            dayLow=Decimal(str(day_low)) if day_low is not None else None,
            fiftyDayAverage=Decimal(str(fifty_day_avg)) if fifty_day_avg is not None else None,
            twoHundredDayAverage=Decimal(str(two_hundred_day_avg)) if two_hundred_day_avg is not None else None,
            fiftyTwoWeekHigh=Decimal(str(fifty_two_week_high)) if fifty_two_week_high is not None else None,
            fiftyTwoWeekLow=Decimal(str(fifty_two_week_low)) if fifty_two_week_low is not None else None
        )

    def get_stock_price(self, symbol: str) -> StockPriceResponse | None:
        """Retrieve current price for a stock symbol from Yahoo Finance.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

        Returns:
            StockPriceResponse if symbol found with price data, None otherwise

        Raises:
            StockInformationIncomplete: When symbol found but current price unavailable
            Exception: Network errors or unexpected API failures propagate
        """
        try:
            self._logger.debug(f"Fetching data for symbol: {symbol}")

            # Fetch ticker information from Yahoo Finance
            ticker_obj = yf.Ticker(symbol)
            info = ticker_obj.info

            # Check if we got valid data (invalid symbols return minimal/empty info)
            if not info or len(info) <= 3:  # Minimal info indicates invalid symbol
                self._logger.warning(f"No data available for symbol: {symbol}")
                return None

            # Extract required current price with fallback strategies
            current_price = None
            for price_key in ['currentPrice', 'regularMarketPrice', 'previousClose']:
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

    def get_stocks_prices(self, symbols: list[str]) -> list[StockPriceResponse]:
        """Retrieve prices for multiple stock symbols from Yahoo Finance.

        Invalid symbols are silently skipped and warnings are logged.

        Args:
            symbols: List of stock ticker symbols (e.g., ['AAPL', 'GOOGL'])

        Returns:
            List of StockPriceResponse objects for successfully fetched symbols.
            Empty list if all symbols are invalid or symbols list is empty.
        """
        if not symbols:
            return []

        try:
            self._logger.debug(f"Fetching batch data for symbols: {symbols}")

            # Use yfinance Tickers API for batch fetching
            tickers = yf.Tickers(' '.join(symbols))
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
                    for price_key in ['currentPrice', 'regularMarketPrice', 'previousClose']:
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

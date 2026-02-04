from decimal import Decimal
from unittest.mock import Mock, patch
import pytest

from pryces.infrastructure.providers import YahooFinanceProvider
from pryces.application.providers import StockPriceResponse
from pryces.application.exceptions import StockInformationIncomplete


class TestYahooFinanceProviderGetStocksPrices:
    def setup_method(self):
        self.provider = YahooFinanceProvider()

    def _create_mock_ticker_info(self, symbol, valid=True, has_price=True):
        if not valid:
            # Invalid symbols return minimal info
            return {'symbol': symbol, 'quoteType': 'EQUITY'}

        info = {
            'symbol': symbol,
            'quoteType': 'EQUITY',
            'longName': f'{symbol} Inc.',
            'currency': 'USD',
            'regularMarketPrice': 150.25 if has_price else None,
            'previousClose': 148.50,
            'open': 149.00,
            'dayHigh': 151.00,
            'dayLow': 148.00,
            'fiftyDayAverage': 145.50,
            'twoHundredDayAverage': 140.00,
            'fiftyTwoWeekHigh': 180.00,
            'fiftyTwoWeekLow': 120.00,
        }
        return info

    @patch('pryces.infrastructure.providers.yf.Tickers')
    def test_get_stocks_prices_with_valid_symbols_returns_all_responses(self, mock_tickers_class):
        mock_ticker_aapl = Mock()
        mock_ticker_aapl.info = self._create_mock_ticker_info('AAPL')

        mock_ticker_googl = Mock()
        mock_ticker_googl.info = self._create_mock_ticker_info('GOOGL')

        mock_tickers = Mock()
        mock_tickers.tickers = {
            'AAPL': mock_ticker_aapl,
            'GOOGL': mock_ticker_googl
        }
        mock_tickers_class.return_value = mock_tickers

        result = self.provider.get_stocks_prices(['AAPL', 'GOOGL'])

        assert len(result) == 2
        assert result[0].symbol == 'AAPL'
        assert result[1].symbol == 'GOOGL'
        assert isinstance(result[0].currentPrice, Decimal)
        assert isinstance(result[1].currentPrice, Decimal)
        mock_tickers_class.assert_called_once_with('AAPL GOOGL')

    @patch('pryces.infrastructure.providers.yf.Tickers')
    def test_get_stocks_prices_with_invalid_symbols_skips_them(self, mock_tickers_class):
        mock_ticker_aapl = Mock()
        mock_ticker_aapl.info = self._create_mock_ticker_info('AAPL', valid=True)

        mock_ticker_invalid = Mock()
        mock_ticker_invalid.info = self._create_mock_ticker_info('INVALID', valid=False)

        mock_tickers = Mock()
        mock_tickers.tickers = {
            'AAPL': mock_ticker_aapl,
            'INVALID': mock_ticker_invalid
        }
        mock_tickers_class.return_value = mock_tickers

        result = self.provider.get_stocks_prices(['AAPL', 'INVALID'])

        assert len(result) == 1
        assert result[0].symbol == 'AAPL'

    @patch('pryces.infrastructure.providers.yf.Tickers')
    def test_get_stocks_prices_with_all_invalid_returns_empty_list(self, mock_tickers_class):
        mock_ticker_invalid1 = Mock()
        mock_ticker_invalid1.info = self._create_mock_ticker_info('INVALID1', valid=False)

        mock_ticker_invalid2 = Mock()
        mock_ticker_invalid2.info = self._create_mock_ticker_info('INVALID2', valid=False)

        mock_tickers = Mock()
        mock_tickers.tickers = {
            'INVALID1': mock_ticker_invalid1,
            'INVALID2': mock_ticker_invalid2
        }
        mock_tickers_class.return_value = mock_tickers

        result = self.provider.get_stocks_prices(['INVALID1', 'INVALID2'])

        assert len(result) == 0
        assert result == []

    def test_get_stocks_prices_with_empty_input_returns_empty_list(self):
        result = self.provider.get_stocks_prices([])

        assert len(result) == 0
        assert result == []

    @patch('pryces.infrastructure.providers.yf.Tickers')
    def test_get_stocks_prices_with_duplicate_symbols(self, mock_tickers_class):
        mock_ticker_aapl = Mock()
        mock_ticker_aapl.info = self._create_mock_ticker_info('AAPL')

        mock_tickers = Mock()
        mock_tickers.tickers = {'AAPL': mock_ticker_aapl}
        mock_tickers_class.return_value = mock_tickers

        result = self.provider.get_stocks_prices(['AAPL', 'AAPL'])

        assert len(result) == 2
        assert result[0].symbol == 'AAPL'
        assert result[1].symbol == 'AAPL'

    @patch('pryces.infrastructure.providers.yf.Tickers')
    def test_get_stocks_prices_preserves_decimal_precision(self, mock_tickers_class):
        mock_ticker = Mock()
        mock_ticker.info = {
            'symbol': 'AAPL',
            'quoteType': 'EQUITY',
            'longName': 'Apple Inc.',
            'currency': 'USD',
            'regularMarketPrice': 150.256789,
            'previousClose': 148.50,
            'open': 149.00,
            'dayHigh': 151.00,
            'dayLow': 148.00,
        }

        mock_tickers = Mock()
        mock_tickers.tickers = {'AAPL': mock_ticker}
        mock_tickers_class.return_value = mock_tickers

        result = self.provider.get_stocks_prices(['AAPL'])

        assert len(result) == 1
        assert isinstance(result[0].currentPrice, Decimal)
        assert str(result[0].currentPrice) == '150.256789'

    @patch('pryces.infrastructure.providers.yf.Tickers')
    def test_get_stocks_prices_includes_all_optional_fields(self, mock_tickers_class):
        mock_ticker = Mock()
        mock_ticker.info = self._create_mock_ticker_info('AAPL')

        mock_tickers = Mock()
        mock_tickers.tickers = {'AAPL': mock_ticker}
        mock_tickers_class.return_value = mock_tickers

        result = self.provider.get_stocks_prices(['AAPL'])

        assert len(result) == 1
        response = result[0]
        assert response.name == 'AAPL Inc.'
        assert response.currency == 'USD'
        assert response.previousClosePrice == Decimal('148.50')
        assert response.openPrice == Decimal('149.00')
        assert response.dayHigh == Decimal('151.00')
        assert response.dayLow == Decimal('148.00')
        assert response.fiftyDayAverage == Decimal('145.50')
        assert response.twoHundredDayAverage == Decimal('140.00')
        assert response.fiftyTwoWeekHigh == Decimal('180.00')
        assert response.fiftyTwoWeekLow == Decimal('120.00')

    @patch('pryces.infrastructure.providers.yf.Tickers')
    def test_get_stocks_prices_handles_mixed_case_symbols(self, mock_tickers_class):
        mock_ticker = Mock()
        mock_ticker.info = self._create_mock_ticker_info('aapl')

        mock_tickers = Mock()
        mock_tickers.tickers = {'aapl': mock_ticker}
        mock_tickers_class.return_value = mock_tickers

        result = self.provider.get_stocks_prices(['aapl'])

        assert len(result) == 1
        assert result[0].symbol == 'AAPL'

    @patch('pryces.infrastructure.providers.yf.Tickers')
    def test_get_stocks_prices_skips_symbols_without_price(self, mock_tickers_class):
        mock_ticker_valid = Mock()
        mock_ticker_valid.info = self._create_mock_ticker_info('AAPL', valid=True, has_price=True)

        mock_ticker_no_price = Mock()
        info_no_price = self._create_mock_ticker_info('GOOGL', valid=True, has_price=False)
        # Remove all price fallback fields
        info_no_price['currentPrice'] = None
        info_no_price['regularMarketPrice'] = None
        info_no_price['previousClose'] = None
        mock_ticker_no_price.info = info_no_price

        mock_tickers = Mock()
        mock_tickers.tickers = {
            'AAPL': mock_ticker_valid,
            'GOOGL': mock_ticker_no_price
        }
        mock_tickers_class.return_value = mock_tickers

        result = self.provider.get_stocks_prices(['AAPL', 'GOOGL'])

        assert len(result) == 1
        assert result[0].symbol == 'AAPL'

    @patch('pryces.infrastructure.providers.yf.Tickers')
    def test_get_stocks_prices_handles_individual_symbol_errors(self, mock_tickers_class):
        mock_ticker_valid = Mock()
        mock_ticker_valid.info = self._create_mock_ticker_info('AAPL')

        mock_ticker_error = Mock()
        mock_ticker_error.info = property(Mock(side_effect=Exception("Network error")))

        mock_tickers = Mock()
        mock_tickers.tickers = {
            'AAPL': mock_ticker_valid,
            'ERROR': mock_ticker_error
        }
        mock_tickers_class.return_value = mock_tickers

        result = self.provider.get_stocks_prices(['AAPL', 'ERROR'])

        assert len(result) == 1
        assert result[0].symbol == 'AAPL'

    @patch('pryces.infrastructure.providers.yf.Tickers')
    def test_get_stocks_prices_uses_price_fallback_strategy(self, mock_tickers_class):
        mock_ticker = Mock()
        mock_ticker.info = {
            'symbol': 'AAPL',
            'quoteType': 'EQUITY',
            'longName': 'Apple Inc.',
            'currency': 'USD',
            'currentPrice': None,
            'regularMarketPrice': 150.25,
            'previousClose': 148.50,
        }

        mock_tickers = Mock()
        mock_tickers.tickers = {'AAPL': mock_ticker}
        mock_tickers_class.return_value = mock_tickers

        result = self.provider.get_stocks_prices(['AAPL'])

        assert len(result) == 1
        assert result[0].currentPrice == Decimal('150.25')

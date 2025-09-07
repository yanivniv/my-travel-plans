import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
sys.path.append('.')
from bot.data_fetcher import DataFetcher
import ccxt

class TestDataFetcher(unittest.TestCase):

    @patch('ccxt.kraken')
    def test_fetch_ohlcv_success(self, mock_kraken):
        """Test successful fetching and parsing of OHLCV data."""
        # --- Arrange ---
        # Create a mock exchange instance
        mock_exchange = MagicMock()

        # Define the data that the mock exchange will return
        mock_ohlcv_data = [
            [1609459200000, 100, 105, 95, 102, 1000],
            [1609459260000, 102, 108, 100, 105, 1200],
        ]
        mock_exchange.fetch_ohlcv.return_value = mock_ohlcv_data
        mock_exchange.has = {'fetchOHLCV': True}

        # Make the ccxt.kraken() call return our mock exchange
        mock_kraken.return_value = mock_exchange

        # --- Act ---
        fetcher = DataFetcher(exchange_name='kraken')
        result_df = fetcher.fetch_ohlcv()

        # --- Assert ---
        self.assertIsNotNone(result_df)
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), 2)
        self.assertEqual(list(result_df.columns), ['open', 'high', 'low', 'close', 'volume'])
        self.assertEqual(result_df['close'].iloc[0], 102)

        # Check that the mock method was called
        mock_exchange.fetch_ohlcv.assert_called_once()

    @patch('ccxt.kraken')
    def test_fetch_ohlcv_exchange_error(self, mock_kraken):
        """Test handling of a ccxt.ExchangeError."""
        # --- Arrange ---
        mock_exchange = MagicMock()
        mock_exchange.fetch_ohlcv.side_effect = ccxt.ExchangeError("Test error")
        mock_exchange.has = {'fetchOHLCV': True}
        mock_kraken.return_value = mock_exchange

        # --- Act ---
        fetcher = DataFetcher(exchange_name='kraken')
        result_df = fetcher.fetch_ohlcv()

        # --- Assert ---
        self.assertIsNone(result_df)

if __name__ == '__main__':
    unittest.main()

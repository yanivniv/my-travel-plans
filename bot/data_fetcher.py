import ccxt
import pandas as pd

class DataFetcher:
    def __init__(self, exchange_name='kraken'):
        """
        Initializes the DataFetcher.

        Args:
            exchange_name (str): The name of the exchange to connect to.
                                 (e.g., 'binance', 'gemini', 'coinbasepro', 'kraken')
        """
        # Note: To trade on a specific exchange, you might need to provide API keys.
        # For now, we are using public endpoints that don't require authentication.
        # Example with API keys:
        # exchange = ccxt.gemini({
        #     'apiKey': 'YOUR_API_KEY',
        #     'secret': 'YOUR_SECRET_KEY',
        #     'options': {
        #         'sandbox': True,  # Use sandbox for paper trading
        #     },
        # })
        self.exchange = getattr(ccxt, exchange_name)()

    def fetch_ohlcv(self, symbol='ETH/USD', timeframe='1h', since=None, limit=100):
        """
        Fetches historical OHLCV data.

        Args:
            symbol (str): The trading symbol to fetch (e.g., 'ETH/USD').
            timeframe (str): The timeframe to fetch (e.g., '1m', '5m', '1h', '1d').
            since (int): The starting timestamp in milliseconds for fetching data.
            limit (int): The maximum number of candles to fetch.

        Returns:
            pandas.DataFrame: A DataFrame with OHLCV data, indexed by timestamp.
                              Returns None if fetching fails.
        """
        if not self.exchange.has['fetchOHLCV']:
            print(f"Exchange {self.exchange.id} does not support fetching OHLCV data.")
            return None

        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except ccxt.NetworkError as e:
            print(f"Network error while fetching OHLCV data: {e}")
            return None
        except ccxt.ExchangeError as e:
            print(f"Exchange error while fetching OHLCV data: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

if __name__ == '__main__':
    # This is an example of how to use the DataFetcher
    fetcher = DataFetcher()

    # Fetch the last 100 hours of ETH/USD data
    eth_data = fetcher.fetch_ohlcv(symbol='ETH/USD', timeframe='1h', limit=100)

    if eth_data is not None:
        print("Successfully fetched ETH/USD data:")
        print(eth_data.head())
        print("\nData information:")
        eth_data.info()
    else:
        print("Failed to fetch data.")

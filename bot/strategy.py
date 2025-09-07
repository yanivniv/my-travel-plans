import pandas as pd
import numpy as np

from .sentiment_analyzer import SentimentAnalyzer

class MovingAverageCrossoverStrategy:
    """
    A moving average crossover trading strategy enhanced with sentiment analysis.
    """
    def __init__(self, short_window=50, long_window=200, sentiment_analyzer=None):
        """
        Initializes the MovingAverageCrossoverStrategy.

        Args:
            short_window (int): The lookback period for the short moving average.
            long_window (int): The lookback period for the long moving average.
            sentiment_analyzer: An instance of SentimentAnalyzer (optional).
        """
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")
        self.short_window = short_window
        self.long_window = long_window
        self.sentiment_analyzer = sentiment_analyzer

    def generate_signals(self, data: pd.DataFrame, symbol: str = 'ETH/USD') -> pd.DataFrame:
        """
        Generates trading signals based on MA crossover and sentiment.

        Args:
            data (pd.DataFrame): A DataFrame containing OHLCV data.
            symbol (str): The trading symbol, used for sentiment analysis.

        Returns:
            pd.DataFrame: The input DataFrame with signals.
        """
        signals = data.copy()
        signals['short_mavg'] = signals['close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['long_mavg'] = signals['close'].rolling(window=self.long_window, min_periods=1).mean()

        # Generate technical signal
        signals['signal'] = 'hold'
        signals.loc[signals['short_mavg'] > signals['long_mavg'], 'signal'] = 'buy'
        signals.loc[signals['short_mavg'] < signals['long_mavg'], 'signal'] = 'sell'

        # If a sentiment analyzer is provided, use it to adjust the signal
        if self.sentiment_analyzer:
            sentiment_score = self.sentiment_analyzer.get_sentiment(symbol)

            # Override buy signal if sentiment is very negative
            if sentiment_score < -0.5:
                signals.loc[signals['signal'] == 'buy', 'signal'] = 'hold'

            # Override sell signal if sentiment is very positive
            if sentiment_score > 0.5:
                signals.loc[signals['signal'] == 'sell', 'signal'] = 'hold'

        return signals

if __name__ == '__main__':
    # Example usage with some dummy data
    # In a real scenario, you would use the DataFetcher to get this data.
    dummy_prices = [100 + i + np.random.randn() * 2 for i in range(250)]
    dummy_data = pd.DataFrame({'close': dummy_prices})

    strategy = MovingAverageCrossoverStrategy(short_window=20, long_window=50)
    signals_df = strategy.generate_signals(dummy_data)

    print("Signals DataFrame:")
    print(signals_df.tail(10))

    # You can also plot the results to visualize the strategy
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 6))
        plt.plot(signals_df['close'], label='Close Price')
        plt.plot(signals_df['short_mavg'], label='Short MA', alpha=0.7)
        plt.plot(signals_df['long_mavg'], label='Long MA', alpha=0.7)

        # Plot buy signals
        plt.plot(signals_df[signals_df['signal'] == 'buy'].index,
                 signals_df['short_mavg'][signals_df['signal'] == 'buy'],
                 '^', markersize=10, color='g', lw=0, label='Buy Signal')

        # Plot sell signals
        plt.plot(signals_df[signals_df['signal'] == 'sell'].index,
                 signals_df['short_mavg'][signals_df['signal'] == 'sell'],
                 'v', markersize=10, color='r', lw=0, label='Sell Signal')

        plt.title('Moving Average Crossover Strategy')
        plt.legend()
        # Saving the plot to a file instead of showing it, as `plt.show()` would block.
        plot_path = 'strategy_visualization.png'
        plt.savefig(plot_path)
        print(f"\nStrategy visualization saved to {plot_path}")

    except ImportError:
        print("\nMatplotlib not found. Skipping plot generation.")
        print("Install it with: pip install matplotlib")

import unittest
from unittest.mock import MagicMock
import pandas as pd
import sys
# Add the root directory to the Python path
sys.path.append('.')
from bot.strategy import MovingAverageCrossoverStrategy

class TestMovingAverageCrossoverStrategy(unittest.TestCase):

    def setUp(self):
        """Set up a sample DataFrame for testing."""
        prices = [10, 20, 30, 40, 50, 40, 30, 20, 10]
        self.data = pd.DataFrame({'close': prices})
        self.base_strategy = MovingAverageCrossoverStrategy(short_window=2, long_window=5)

    def test_generate_signals_no_sentiment(self):
        """Test that signals are generated correctly without sentiment analysis."""
        signals_df = self.base_strategy.generate_signals(self.data)
        expected_signals = ['hold', 'hold', 'buy', 'buy', 'buy', 'buy', 'sell', 'sell', 'sell']
        pd.testing.assert_series_equal(pd.Series(expected_signals, name='signal'), signals_df['signal'], check_names=False)

    def test_sentiment_override_buy_to_hold(self):
        """Test that negative sentiment overrides a buy signal."""
        mock_sentiment_analyzer = MagicMock()
        mock_sentiment_analyzer.get_sentiment.return_value = -0.8 # Very negative

        strategy = MovingAverageCrossoverStrategy(short_window=2, long_window=5, sentiment_analyzer=mock_sentiment_analyzer)
        signals_df = strategy.generate_signals(self.data)

        # The 'buy' signals should now be 'hold'
        expected_signals = ['hold', 'hold', 'hold', 'hold', 'hold', 'hold', 'sell', 'sell', 'sell']
        pd.testing.assert_series_equal(pd.Series(expected_signals, name='signal'), signals_df['signal'], check_names=False)

    def test_sentiment_override_sell_to_hold(self):
        """Test that positive sentiment overrides a sell signal."""
        mock_sentiment_analyzer = MagicMock()
        mock_sentiment_analyzer.get_sentiment.return_value = 0.8 # Very positive

        strategy = MovingAverageCrossoverStrategy(short_window=2, long_window=5, sentiment_analyzer=mock_sentiment_analyzer)
        signals_df = strategy.generate_signals(self.data)

        # The 'sell' signals should now be 'hold'
        expected_signals = ['hold', 'hold', 'buy', 'buy', 'buy', 'buy', 'hold', 'hold', 'hold']
        pd.testing.assert_series_equal(pd.Series(expected_signals, name='signal'), signals_df['signal'], check_names=False)

    def test_short_window_validation(self):
        """Test that the short window must be less than the long window."""
        with self.assertRaises(ValueError):
            MovingAverageCrossoverStrategy(short_window=10, long_window=5)

if __name__ == '__main__':
    unittest.main()

import unittest
import pandas as pd
import sys
sys.path.append('.')
from bot.backtester import Backtester

# Mock strategy for testing
class MockStrategy:
    def __init__(self, signals):
        self.signals = signals

    def generate_signals(self, data, symbol=None): # Add symbol argument
        data['signal'] = self.signals
        return data

class TestBacktester(unittest.TestCase):

    def setUp(self):
        """Set up a sample DataFrame and a mock strategy."""
        self.prices = [100, 110, 120, 110, 100, 90]
        self.data = pd.DataFrame({'close': self.prices})

    def test_buy_and_sell_logic(self):
        """Test a simple buy and sell scenario."""
        signals = ['buy', 'hold', 'hold', 'sell', 'hold', 'hold']
        mock_strategy = MockStrategy(signals)

        backtester = Backtester(mock_strategy, self.data, initial_cash=1000, commission=0.01) # 1% commission
        portfolio = backtester.run(symbol='TEST/USD')

        # Check if trades happened on the right days
        self.assertEqual(portfolio['trades'].iloc[0], 1) # Buy
        self.assertEqual(portfolio['trades'].iloc[1], 0) # Hold
        self.assertEqual(portfolio['trades'].iloc[2], 0) # Hold
        self.assertEqual(portfolio['trades'].iloc[3], 1) # Sell
        self.assertEqual(portfolio['trades'].iloc[4], 0) # Hold
        self.assertEqual(portfolio['trades'].iloc[5], 0) # Hold

        # Check final portfolio value
        # Calculation:
        # Initial cash: 1000
        # Buy at 100 with 1% commission:
        # amount_to_buy = 1000 / (100 * 1.01) = 9.90099
        # holdings_value = 9.90099 * 100 = 990.099
        # After buy, cash is 0, total is 990.099
        # At time of sell, price is 110. Holdings value is 9.90099 * 110 = 1089.1089
        # Sell at 110 with 1% commission:
        # proceeds = 9.90099 * 110 * (1 - 0.01) = 1078.2178
        # Final cash = 1078.2178. Holdings = 0. Total = 1078.2178

        self.assertAlmostEqual(portfolio['total'].iloc[-1], 1078.2178, places=4)

if __name__ == '__main__':
    unittest.main()

import pandas as pd
import numpy as np
import sys
sys.path.append('.')
from bot.data_fetcher import DataFetcher
from bot.strategy import MovingAverageCrossoverStrategy
from bot.backtester import Backtester
import itertools

def run_optimization():
    """
    Runs a parameter optimization for the MovingAverageCrossoverStrategy.
    """
    # 1. Fetch data
    print("Fetching historical data for optimization...")
    fetcher = DataFetcher()
    data = fetcher.fetch_ohlcv(symbol='ETH/USD', timeframe='1d', limit=1000)

    if data is None or data.empty:
        print("Could not fetch data. Aborting optimization.")
        return

    # 2. Define parameter ranges
    short_windows = np.arange(10, 60, 5) # 10, 15, ..., 55
    long_windows = np.arange(50, 250, 10) # 50, 60, ..., 240

    results = []

    # Generate all valid combinations of windows
    param_combinations = list(itertools.product(short_windows, long_windows))
    valid_combinations = [(sw, lw) for sw, lw in param_combinations if sw < lw]

    print(f"Starting optimization for {len(valid_combinations)} parameter combinations...")

    # 3. Loop through parameters and backtest
    for i, (sw, lw) in enumerate(valid_combinations):
        print(f"Testing combination {i+1}/{len(valid_combinations)}: short={sw}, long={lw}", end='\r')
        strategy = MovingAverageCrossoverStrategy(short_window=sw, long_window=lw)
        backtester = Backtester(strategy, data, initial_cash=10000, commission=0.002)
        portfolio = backtester.run()

        final_value = portfolio['total'].iloc[-1]
        total_return = (final_value / backtester.initial_cash) - 1

        results.append({
            'short_window': sw,
            'long_window': lw,
            'return': total_return
        })

    # 4. Analyze results
    if not results:
        print("No results from optimization.")
        return

    results_df = pd.DataFrame(results)

    print("\n\n--- Optimization Complete ---")
    print("Top 5 Best Performing Parameter Combinations:")
    top_5 = results_df.sort_values(by='return', ascending=False).head(5)
    print(top_5)

if __name__ == '__main__':
    run_optimization()

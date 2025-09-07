import pandas as pd

class Backtester:
    """
    A simple backtesting engine for trading strategies.
    """
    def __init__(self, strategy, data, initial_cash=10000, commission=0.001):
        """
        Initializes the Backtester.

        Args:
            strategy: An instance of a trading strategy class.
            data (pd.DataFrame): A DataFrame containing OHLCV data.
            initial_cash (float): The starting cash balance.
            commission (float): The trading commission fee per trade (e.g., 0.001 for 0.1%).
        """
        self.strategy = strategy
        self.data = data
        self.initial_cash = initial_cash
        self.commission = commission
        self.portfolio = None # Will be created in run()

    def _create_initial_portfolio(self, index):
        """Creates the initial portfolio DataFrame."""
        portfolio = pd.DataFrame(index=index)
        portfolio['holdings'] = 0.0  # Total value of asset held
        portfolio['cash'] = float(self.initial_cash)
        portfolio['total'] = float(self.initial_cash)
        portfolio['trades'] = 0  # Number of trades made
        return portfolio

    def run(self, symbol='ETH/USD'):
        """Runs the backtest."""
        self.signals = self.strategy.generate_signals(self.data, symbol)
        self.portfolio = self._create_initial_portfolio(self.signals.index)
        position_shares = 0.0

        for i in range(len(self.signals)):
            close_price = self.signals.loc[self.signals.index[i], 'close']

            # First, carry over cash from the previous period
            if i > 0:
                self.portfolio.loc[self.signals.index[i], 'cash'] = self.portfolio.loc[self.signals.index[i-1], 'cash']

            # Update holdings value based on current price
            self.portfolio.loc[self.signals.index[i], 'holdings'] = position_shares * close_price

            signal = self.signals.loc[self.signals.index[i], 'signal']

            if signal == 'buy' and position_shares == 0:
                # Buy signal and not in a position
                cash_to_use = self.portfolio.loc[self.signals.index[i], 'cash']
                shares_to_buy = cash_to_use / (close_price * (1 + self.commission))

                position_shares = shares_to_buy
                self.portfolio.loc[self.signals.index[i], 'cash'] = 0.0
                self.portfolio.loc[self.signals.index[i], 'holdings'] = position_shares * close_price
                self.portfolio.loc[self.signals.index[i], 'trades'] = 1

            elif signal == 'sell' and position_shares > 0:
                # Sell signal and in a position
                proceeds = position_shares * close_price * (1 - self.commission)

                self.portfolio.loc[self.signals.index[i], 'cash'] += proceeds
                self.portfolio.loc[self.signals.index[i], 'holdings'] = 0
                position_shares = 0
                self.portfolio.loc[self.signals.index[i], 'trades'] = 1

            # Update total portfolio value
            self.portfolio.loc[self.signals.index[i], 'total'] = self.portfolio.loc[self.signals.index[i], 'cash'] + self.portfolio.loc[self.signals.index[i], 'holdings']

        return self.portfolio

    def print_performance(self):
        """Prints a summary of the backtest performance."""
        final_portfolio_value = self.portfolio['total'].iloc[-1]
        total_return = (final_portfolio_value / self.initial_cash) - 1
        total_trades = self.portfolio['trades'].sum()

        print("Backtest Performance Summary:")
        print("-----------------------------")
        print(f"Initial Portfolio Value: ${self.initial_cash:,.2f}")
        print(f"Final Portfolio Value:   ${final_portfolio_value:,.2f}")
        print(f"Total Return:            {total_return:.2%}")
        print(f"Total Trades:            {total_trades}")
        print("-----------------------------")


if __name__ == '__main__':
    from data_fetcher import DataFetcher
    from strategy import MovingAverageCrossoverStrategy

    # 1. Fetch data
    print("Fetching data...")
    fetcher = DataFetcher()
    # Let's get more data for a meaningful backtest
    ohlcv_data = fetcher.fetch_ohlcv(symbol='ETH/USD', timeframe='1d', limit=500)

    if ohlcv_data is not None and not ohlcv_data.empty:
        # 2. Initialize strategy
        # Using optimal parameters
        strategy = MovingAverageCrossoverStrategy(short_window=25, long_window=70)

        # 3. Run backtest
        print("Running backtest with optimized parameters...")
        backtester = Backtester(strategy, ohlcv_data, initial_cash=10000, commission=0.002)
        portfolio = backtester.run(symbol='ETH/USD')

        # 4. Print performance
        backtester.print_performance()

        # 5. (Optional) Plot results
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(12, 6))
            plt.plot(portfolio['total'], label='Portfolio Value')
            plt.title('Portfolio Value Over Time')
            plt.legend()
            plot_path = 'portfolio_performance.png'
            plt.savefig(plot_path)
            print(f"\nPortfolio performance plot saved to {plot_path}")
        except ImportError:
            print("\nMatplotlib not found. Skipping plot generation.")

    else:
        print("Could not fetch data for backtest.")

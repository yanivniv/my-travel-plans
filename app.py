from flask import Flask, render_template
from bot.data_fetcher import DataFetcher
from bot.strategy import MovingAverageCrossoverStrategy
from bot.backtester import Backtester
from bot.sentiment_analyzer import SentimentAnalyzer
import os

app = Flask(__name__)

@app.route('/')
def home():
    """
    Main route that runs the backtest and displays the results.
    """
    # --- Run the backtest ---
    fetcher = DataFetcher()
    ohlcv_data = fetcher.fetch_ohlcv(symbol='ETH/USD', timeframe='1d', limit=500)

    if ohlcv_data is None or ohlcv_data.empty:
        return "Error: Could not fetch data for the backtest.", 500

    # Initialize sentiment analyzer
    sentiment_analyzer = SentimentAnalyzer()

    # Initialize strategy with the sentiment analyzer and optimal parameters
    strategy = MovingAverageCrossoverStrategy(
        short_window=25,
        long_window=70,
        sentiment_analyzer=sentiment_analyzer
    )

    backtester = Backtester(strategy, ohlcv_data, initial_cash=10000, commission=0.002)
    portfolio = backtester.run(symbol='ETH/USD')

    # --- Prepare results for the template ---
    final_value = portfolio['total'].iloc[-1]
    total_return = (final_value / backtester.initial_cash) - 1
    total_trades = portfolio['trades'].sum()

    results = {
        'initial_cash': f"${backtester.initial_cash:,.2f}",
        'final_value': f"${final_value:,.2f}",
        'total_return': f"{total_return:.2%}",
        'total_trades': total_trades
    }

    # --- Generate and save the plot ---
    # The plot will be saved in the `static` directory for Flask to serve it.
    if not os.path.exists('static'):
        os.makedirs('static')
    plot_path = 'static/portfolio_performance.png'

    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 6))
        plt.plot(portfolio['total'], label='Portfolio Value')
        plt.title('Portfolio Value Over Time')
        plt.legend()
        plt.savefig(plot_path)
        plt.close() # Close the plot to free up memory
    except ImportError:
        plot_path = None # Or a placeholder image path

    return render_template('index.html', results=results, plot_image=plot_path)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

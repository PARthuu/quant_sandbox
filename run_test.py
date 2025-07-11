from src.data_loader import load_yfinance_data, load_crypto_data
import src.strategy as strategy
from src.backtester import Backtester
from src.metrics import calculate_metrics
from src.tracker import save_experiment
from src.visualizer import plot_equity_curve, plot_signals, new_plot_signals, plot_trend


df = load_crypto_data("BTC/USDT", timeframe="1m", limit=10000)  # or load_yfinance_data(...)

strat = strategy.BollingerBandStrategy(df)
signals = strat.generate_signals()

bt = Backtester(df, signals)
results = bt.run()
metrics = calculate_metrics(results)

# save_experiment(metrics, tag="SMA_20_50_BTC")
new_plot_signals(df, signals)
plot_equity_curve(results)

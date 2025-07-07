from src.data_loader import load_yfinance_data
from src.visualizer import plot_equity_curve
from src.strategy import SMACrossoverStrategy as st
from src.backtester import Backtester
from src.metrics import calculate_metrics
from src.visualizer import plot_signals, plot_equity_curve, plot_trend
from src.tracker import save_experiment

df = load_yfinance_data("AAPL", "2025-07-03", "2025-07-04", "1m")

# print(df)
# plot_trend(df)
strategy = st(df)
signals = strategy.generate_signals()
bt = Backtester(df, signals)
results = bt.run()
metrics = calculate_metrics(results)

save_experiment(metrics, tag="SMA_20_50_AAPL")
plot_signals(df, signals)
plot_equity_curve(results)
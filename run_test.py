from src.data_loader import load_data
import src.strategy as strategy
from src.backtester import Backtester
from src.metrics import calculate_metrics
from src.tracker import save_experiment
from src.visualizer import show_metrics, plot_results, plot_signals


df = load_data("BTC")

strat = strategy.BollingerBandStrategy(df)
signals = strat.generate_signals()

bt = Backtester(df, signals)
results = bt.run()
metrics = calculate_metrics(results)
show_metrics(metrics)

plot_results(df, signals, results)
# save_experiment(metrics, tag="SMA_20_50_BTC")

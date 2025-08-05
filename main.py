from src.data_loader import load_file, select_to_load_data
from src.strategy import BollingerBandStrategy as strategy
from src.backtester import Backtester
from src.metrics import calculate_metrics
from src.tracker import save_experiment
from src.visualizer import show_metrics, plot_results


df = select_to_load_data()

strat = strategy(df)
signals = strat.generate_signals()

bt = Backtester(df, signals)
results = bt.run()
metrics = calculate_metrics(results)
# show_metrics(metrics)
plot_results(df, signals, results)
# save_experiment(metrics, tag="SMA_20_50_BTC")
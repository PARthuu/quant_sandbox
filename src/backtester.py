import pandas as pd

class Backtester:
    def __init__(self, data: pd.DataFrame, signals: pd.DataFrame, capital: float = 10000):
        self.data = data.copy()
        self.signals = signals.copy()
        self.capital = capital

    def run(self):
        df = self.data.copy()
        df['signal'] = self.signals['signal']
        df['positions'] = self.signals['positions']
        df['return'] = df['close'].pct_change().fillna(0)
        df['strategy_return'] = df['signal'].shift(1).fillna(0) * df['return']
        df['equity_curve'] = (1 + df['strategy_return']).cumprod() * self.capital
        return df

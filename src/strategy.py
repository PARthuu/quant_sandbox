from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import pandas as pd

class Strategy:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.signals = pd.DataFrame(index=self.data.index)


class SMACrossoverStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, short_window: int = 20, long_window: int = 50):
        super().__init__(data)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        self.signals['short_ma'] = self.data['close'].rolling(self.short_window).mean()
        self.signals['long_ma'] = self.data['close'].rolling(self.long_window).mean()
        self.signals['signal'] = 0
        self.signals.loc[self.signals.index[self.short_window:], 'signal'] = (
            self.signals['short_ma'].iloc[self.short_window:] > self.signals['long_ma'].iloc[self.short_window:]
        ).astype(int)
        self.signals['positions'] = self.signals['signal'].diff()
        return self.signals
    
class EMACrossoverStrategy(Strategy):
    def __init__(self, data, short_window=20, long_window=50):
        super().__init__(data)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        self.signals['short_ema'] = self.data['close'].ewm(span=self.short_window).mean()
        self.signals['long_ema'] = self.data['close'].ewm(span=self.long_window).mean()
        self.signals['signal'] = (self.signals['short_ema'] > self.signals['long_ema']).astype(int)
        self.signals['positions'] = self.signals['signal'].diff()
        return self.signals

class RSIStrategy(Strategy):
    def __init__(self, data, rsi_period=14, overbought=70, oversold=30):
        super().__init__(data)
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self):
        rsi = RSIIndicator(self.data['close'], window=self.rsi_period).rsi()
        self.signals['rsi'] = rsi
        self.signals['signal'] = 0
        self.signals.loc[rsi < self.oversold, 'signal'] = 1
        self.signals.loc[rsi > self.overbought, 'signal'] = 0
        self.signals['positions'] = self.signals['signal'].diff()
        return self.signals

class BollingerBandStrategy(Strategy):
    def __init__(self, data, window=20, std_dev=2):
        super().__init__(data)
        self.window = window
        self.std_dev = std_dev

    def generate_signals(self):
        bb = BollingerBands(close=self.data['close'], window=self.window, window_dev=self.std_dev)
        self.signals['bb_upper'] = bb.bollinger_hband()
        self.signals['bb_lower'] = bb.bollinger_lband()
        self.signals['signal'] = 0
        self.signals.loc[self.data['close'] < self.signals['bb_lower'], 'signal'] = 1
        self.signals.loc[self.data['close'] > self.signals['bb_upper'], 'signal'] = 0
        self.signals['positions'] = self.signals['signal'].diff()
        return self.signals

class CombinedStrategy(Strategy):
    def __init__(self, data, strat_a, strat_b, logic='AND'):
        super().__init__(data)
        self.strat_a = strat_a(data)
        self.strat_b = strat_b(data)
        self.logic = logic

    def generate_signals(self):
        a = self.strat_a.generate_signals()['signal']
        b = self.strat_b.generate_signals()['signal']
        self.signals['signal'] = ((a & b) if self.logic == 'AND' else (a | b)).astype(int)
        self.signals['positions'] = self.signals['signal'].diff()
        return self.signals

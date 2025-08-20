from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import pandas as pd

pd.set_option('display.max_rows', None)

STRATEGY_REGISTRY = {}

def register_strategy(cls):
    STRATEGY_REGISTRY[cls.__name__] = cls
    return cls

class Strategy:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.signals = pd.DataFrame(index=self.data.index)

@register_strategy
class SMACrossoverStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, short_window: int = 20, long_window: int = 50):
        super().__init__(data)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        self.signals['low'] = self.data['close'].rolling(self.short_window).mean()
        self.signals['high'] = self.data['close'].rolling(self.long_window).mean()
        self.signals['signal'] = 0
        self.signals.loc[self.signals.index[self.short_window:], 'signal'] = (
            (self.signals['low'].iloc[self.short_window:] > self.signals['high'].iloc[self.short_window:]) * 2 - 1
        )
        self.signals['positions'] = self.signals['signal'].diff().clip(1, -1)
        return self.signals
@register_strategy    
class EMACrossoverStrategy(Strategy):
    def __init__(self, data, short_window=20, long_window=50):
        super().__init__(data)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        self.signals['low'] = self.data['close'].ewm(span=self.short_window).mean()
        self.signals['high'] = self.data['close'].ewm(span=self.long_window).mean()
        self.signals['signal'] = -1
        self.signals['signal'] = ((self.signals['low'] > self.signals['high']) * 2 - 1)
        self.signals['positions'] = self.signals['signal'].diff().clip(1, -1)
        return self.signals
@register_strategy
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
        self.signals['low'] = self.oversold
        self.signals['high'] = self.overbought
        # self.signals['mid'] = self.signals['rsi']
        return self.signals
@register_strategy
class BollingerBandStrategy(Strategy):
    def __init__(self, data, window=20, std_dev=3):
        super().__init__(data)
        self.window = window
        self.std_dev = std_dev
        self.buy = 0

    def generate_signals(self):
        bb = BollingerBands(close=self.data['close'], window=self.window, window_dev=self.std_dev)
        self.signals['mid'] = bb.bollinger_mavg()
        self.signals['high'] = bb.bollinger_hband()
        self.signals['low'] = bb.bollinger_lband()

        # Generate entry signals only on confirmation (re-entry into band)
        for i in range(1, len(self.signals)):
            # Buy when price was below lower band and comes back above it
            if (self.buy == 0 or self.buy == -1) and self.data['close'].iloc[i-1] < self.signals['low'].iloc[i-1] and self.data['close'].iloc[i] > self.signals['low'].iloc[i]:
                self.buy = 1

            # Sell when price was above upper band and comes back below it
            if (self.buy == 0 or self.buy == 1) and self.data['close'].iloc[i-1] > self.signals['high'].iloc[i-1] and self.data['close'].iloc[i] < self.signals['high'].iloc[i]:
                self.buy = -1

            self.signals.at[self.data.index[i], 'signal'] = self.buy

        self.signals['positions'] = self.signals['signal'].diff().clip(lower=-1, upper=1)
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
@register_strategy
class SwingStrategy(Strategy):
    def __init__(self, data, cooldown=1):
        super().__init__(data)
        self.cooldown = cooldown

    def generate_signals(self):
        self.signals['close'] = self.data['close']
        
        # Generate basic signal: 1 for up, -1 for down
        self.signals['raw_signal'] = (self.signals['close'].diff() > 0).astype(int) * 2 - 1
        
        # Initialize signal column with zeros
        self.signals['signal'] = 0
        last_trade_index = -self.cooldown  # Initialize far in the past
        
        for i in range(1, len(self.signals)):
            if (i - last_trade_index) >= self.cooldown:
                self.signals.iloc[i, self.signals.columns.get_loc('signal')] = self.signals.iloc[i, self.signals.columns.get_loc('raw_signal')]
                last_trade_index = i
            else:
                self.signals.iloc[i, self.signals.columns.get_loc('signal')] = self.signals.iloc[i - 1, self.signals.columns.get_loc('signal')]


        # Calculate position changes (1 for new long, -1 for new short)
        self.signals['positions'] = self.signals['signal'].diff().clip(lower=-1, upper=1)
        
        return self.signals
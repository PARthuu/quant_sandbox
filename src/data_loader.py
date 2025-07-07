import yfinance as yf
import pandas as pd
from ccxt import binance

def load_yfinance_data(ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=False)
    df = df.rename(columns={
        'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adj_close', 'Volume': 'volume'
    })
    df.index.name = 'datetime'
    return df.dropna()

def load_crypto_data(symbol: str = 'BTC/USDT', timeframe: str = '1h', limit: int = 500) -> pd.DataFrame:
    exchange = binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('datetime', inplace=True)
    return df[['open', 'high', 'low', 'close', 'volume']]
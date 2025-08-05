import yfinance as yf
import pandas as pd
from ccxt import binance
from datetime import datetime
import os
from InquirerPy import inquirer

def load_yfinance_data(ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=False)

    # If multiple tickers, reduce MultiIndex to single ticker
    if isinstance(df.columns, pd.MultiIndex):
        df = df.xs(ticker, axis=1, level=1)

    df = df.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Adj Close': 'adj_close',
        'Volume': 'volume'
    })

    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = 'datetime'
    df = df[['open', 'high', 'low', 'close', 'adj_close', 'volume']]
    return df.dropna()

def load_crypto_data(symbol: str = 'BTC/USDT', timeframe: str = '1s', limit: int = 1000) -> pd.DataFrame:
    exchange = binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)  # Ensure UTC
    df.set_index('datetime', inplace=True)
    df['adj_close'] = df['close']  # Crypto has no real 'adj_close', so we mirror 'close'
    df = df[['open', 'high', 'low', 'close', 'adj_close', 'volume']]
    return df.dropna()

def save_data(df: pd.DataFrame, filename: str):
    """
    Saves the given DataFrame to a Parquet file.
    """
    df.to_parquet('data/' + filename + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), index=True)
    print(f"Data saved to data/{filename}")

def load_file(filename: str) -> pd.DataFrame:
    """
    Loads a DataFrame from a Parquet file.
    """
    df = pd.read_parquet('data/' + filename)
    print(f"Data loaded from data/{filename}")
    return df

def select_to_load_data(directory='data/') -> pd.DataFrame:
    """
    Allows user to interactively select a file using fuzzy search
    and loads the selected Parquet file as a DataFrame.
    """
    files = sorted(os.listdir(directory))

    filename = inquirer.fuzzy(
        message="🔍 Type to filter and select a data file:",
        choices=files,
        max_height="70%",  # scrollable if too many results
        default=None,
        multiselect=False,
        validate=lambda result: result in files,
    ).execute()

    path = os.path.join(directory, filename)
    df = pd.read_parquet(path)
    print(f"✅ Data loaded from {path}")
    return df


'''
# ---------- Code for Data Generation and Example ----------
asset = "DAI/USDT"
# df = load_yfinance_data(asset, "2025-07-03", "2025-07-04", "1m")
df = load_crypto_data(asset, timeframe="1m", limit=10000)

save_data(df, asset)
'''
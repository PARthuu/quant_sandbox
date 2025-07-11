import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def plot_trend(df: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Plot Price and Moving Averages
    ax1.plot(df['close'], label='Price', alpha=0.5, color='blue')

    plt.plot(df['open'], label='Open Price', alpha=0.5)
    plt.plot(df['close'], label='Close Price', alpha=0.5)
    plt.plot(df['high'], label='High Price',linestyle='--', alpha=0.5)
    plt.plot(df['low'], label='Low Price',linestyle='--', alpha=0.5)

    plt.title('Price Trend')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)

    # Secondary Y-axis for Volume
    ax2 = ax1.twinx()
    ax2.bar(df.index, df['volume'], width=0.02, alpha=0.2, color='gray', label='Volume')
    ax2.set_ylabel('Volume')

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.tight_layout()
    plt.show()



def plot_equity_curve(df: pd.DataFrame):
    plt.figure(figsize=(12, 6))
    plt.plot(df['equity_curve'], label='Equity Curve', color='blue')
    plt.title('Equity Curve')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_signals(df: pd.DataFrame, signals: pd.DataFrame):
    plt.figure(figsize=(14, 6))
    plt.plot(df['close'], label='Price', alpha=0.5)
    plt.plot(signals['short_ma'], label='Short MA', linestyle='--', color='green')
    plt.plot(signals['long_ma'], label='Long MA', linestyle='--', color='red')
    buy_signals = signals[signals['positions'] == 1.0]
    sell_signals = signals[signals['positions'] == -1.0]
    plt.plot(buy_signals.index, df.loc[buy_signals.index]['close'], '^', markersize=8, color='g', label='Buy')
    plt.plot(sell_signals.index, df.loc[sell_signals.index]['close'], 'v', markersize=8, color='r', label='Sell')
    plt.title('Trading Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def new_plot_signals(df: pd.DataFrame, signals: pd.DataFrame):
    # Convert datetime index to matplotlib's numeric format
    df = df.copy()
    df['date_num'] = mdates.date2num(df.index.to_pydatetime())

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    # ---- Price and Buy/Sell Signals (Top Plot) ----
    ax1.plot(df.index, df['close'], label='Price', alpha=0.5, color='blue')

    # Plot Buy/Sell signals
    buy_signals = signals[signals['positions'] == 1.0]
    sell_signals = signals[signals['positions'] == -1.0]
    ax1.plot(buy_signals.index, df.loc[buy_signals.index, 'close'], '^', markersize=8, color='g', label='Buy')
    ax1.plot(sell_signals.index, df.loc[sell_signals.index, 'close'], 'v', markersize=8, color='r', label='Sell')

    ax1.set_title('Trading Signals and Price')
    ax1.set_ylabel('Price')
    ax1.grid(True)
    ax1.legend(loc='upper left')

    # ---- Volume Bars (Bottom Plot) ----
    # Use numeric x-values for bar chart to fix alignment
    ax2.bar(df['date_num'], df['volume'], width=0.0005, alpha=0.4, color='black', align='center')
    ax2.set_ylabel('Volume')
    ax2.set_xlabel('Date')
    ax2.grid(True)

    # Format x-axis with dates
    ax2.xaxis_date()
    fig.autofmt_xdate()  # Auto-rotate date labels

    plt.tight_layout()
    plt.show()
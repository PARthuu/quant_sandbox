import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

plt.style.use('dark_background')

def show_metrics(data):
    # KPI benchmark ranges as strings (for display)
    benchmarks = {
        'Sharpe Ratio':      ['< 0', '0 to 1', '> 1'],
        'Sortino Ratio':     ['< 0', '0 to 1.5', '> 1.5'],
        'Max Drawdown':      ['< -20%', '-20% to -5%', '> -5%'],
        'Total Return':      ['< 0', '0 to 15%', '> 15%'],
        'CAGR':              ['< 0', '0 to 10%', '> 10%'],
        'Volatility':        ['> 20%', '10% to 20%', '< 10%'],
        'Win Rate':          ['< 40%', '40% to 60%', '> 60%'],
        'Avg Gain':          ['< Avg Loss', '≈ Avg Loss', '> Avg Loss'],
        'Avg Loss':          ['> Avg Gain', '≈ Avg Gain', '< Avg Gain'],
        'Profit Factor':     ['< 1', '1 to 1.3', '> 1.3'],
        'Expectancy':        ['< 0', '0 to 0.002', '> 0.002']
    }

    # Function to determine category for each KPI value
    def categorize(kpi, value):
        if kpi == 'Sharpe Ratio':
            if value > 1: return 'Very Good'
            elif value >= 0: return 'Good'
            else: return 'Bad'
        elif kpi == 'Sortino Ratio':
            if value > 1.5: return 'Very Good'
            elif value >= 0: return 'Good'
            else: return 'Bad'
        elif kpi == 'Max Drawdown':
            if value > -0.05: return 'Very Good'
            elif value > -0.20: return 'Good'
            else: return 'Bad'
        elif kpi == 'Total Return':
            if value > 0.15: return 'Very Good'
            elif value >= 0: return 'Good'
            else: return 'Bad'
        elif kpi == 'CAGR':
            if value > 0.10: return 'Very Good'
            elif value >= 0: return 'Good'
            else: return 'Bad'
        elif kpi == 'Volatility':
            if value < 0.10: return 'Very Good'
            elif value < 0.20: return 'Good'
            else: return 'Bad'  # high risk
        elif kpi == 'Win Rate':
            if value > 0.60: return 'Very Good'
            elif value >= 0.40: return 'Good'
            else: return 'Bad'
        elif kpi == 'Avg Gain':
            # Comparing Avg Gain to Avg Loss is contextual, mark as 'N/A'
            return 'N/A'
        elif kpi == 'Avg Loss':
            return 'N/A'
        elif kpi == 'Profit Factor':
            if value > 1.3: return 'Very Good'
            elif value >= 1: return 'Good'
            else: return 'Bad'
        elif kpi == 'Expectancy':
            if value > 0.002: return 'Very Good'
            elif value >= 0: return 'Good'
            else: return 'Bad'
        return 'N/A'

    # Build DataFrame rows with categorization
    rows = []
    for kpi, value in data.items():
        bad, good, very_good = benchmarks[kpi]
        category = categorize(kpi, value)
        rows.append({
            'KPI': kpi,
            'Value': round(value, 4),
            'Category': category,
            'Bad': bad,
            'Good': good,
            'Very Good': very_good
        })

    df = pd.DataFrame(rows)

    # Reorder columns: KPI, Value, Category, Bad, Good, Very Good
    df = df[['KPI', 'Value', 'Category', 'Bad', 'Good', 'Very Good']]

    # Show table
    print(df.to_string(index=False))

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


def plot_results(df: pd.DataFrame, signals: pd.DataFrame, results: pd.DataFrame):
    # Convert datetime index to matplotlib's numeric format
    df = df.copy()
    df['date_num'] = mdates.date2num(df.index.to_pydatetime())

    # Apply dark theme
    background_color = '#121212'
    grid_color = '#333333'
    text_color = 'white'

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 9),
                                        sharex=True,
                                        gridspec_kw={'height_ratios': [3, 1, 1]},
                                        facecolor=background_color)

    # Apply dark theme settings to axes
    for ax in (ax1, ax2, ax3):
        ax.set_facecolor(background_color)
        ax.tick_params(colors=text_color)
        ax.yaxis.label.set_color(text_color)
        ax.xaxis.label.set_color(text_color)
        ax.grid(True, color=grid_color)

    # ---- Price and Buy/Sell Signals (Top Plot) ----
    ax1.plot(df.index, df['close'], label='Price', alpha=0.7, color='lime')

    buy_signals = signals[signals['positions'] == 1.0]
    sell_signals = signals[signals['positions'] == -1.0]
    ax1.plot(buy_signals.index, df.loc[buy_signals.index, 'close'], '^', markersize=8, color='lightgreen', label='Buy')
    ax1.plot(sell_signals.index, df.loc[sell_signals.index, 'close'], 'v', markersize=8, color='red', label='Sell')

    ax1.set_title('Trading Signals and Price', color=text_color)
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left', facecolor=background_color, edgecolor=grid_color, labelcolor=text_color)

    # ---- Volume Bars (Middle Plot) ----
    ax2.bar(df['date_num'], df['volume'], width=0.0006, alpha=0.6, color='cyan', align='center')
    ax2.set_ylabel('Volume')

    # ---- Equity Curve (Bottom Plot) ----
    if 'equity_curve' in results.columns:
        ax3.plot(results.index, results['equity_curve'], label='Equity Curve', color='deepskyblue')
        ax3.set_ylabel('Portfolio Value')
        ax3.set_xlabel('Date')
        ax3.legend(facecolor=background_color, edgecolor=grid_color, labelcolor=text_color)
    else:
        ax3.text(0.5, 0.5, 'No Equity Curve Found in DataFrame',
                 transform=ax3.transAxes, ha='center', va='center',
                 fontsize=12, color='orange')
        ax3.set_axis_off()

    # Format x-axis
    ax3.xaxis_date()
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.show()
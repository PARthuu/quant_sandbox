import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd

# Settings
vol_width = 0.0006

# Apply dark theme
plt.style.use('dark_background')
background_color = '#121212'
grid_color = '#333333'
text_color = 'white'


def plot_results(df: pd.DataFrame, signals: pd.DataFrame, results: pd.DataFrame):
    df = df.copy()
    df.index = pd.to_datetime(df.index)

    results = results.copy()
    results.index = pd.to_datetime(results.index)
    results = results[results.index.isin(df.index)]

    # ---- Add Buy/Sell markers at actual close prices ----
    df['Buy_marker'] = float('nan')
    df['Sell_marker'] = float('nan')

    buy_signals = signals[signals.get('positions', pd.Series()) == 1.0]
    sell_signals = signals[signals.get('positions', pd.Series()) == -1.0]

    df.loc[buy_signals.index, 'Buy_marker'] = df.loc[buy_signals.index, 'close']
    df.loc[sell_signals.index, 'Sell_marker'] = df.loc[sell_signals.index, 'close']

    # ---- Set up figure layout ----
    fig = plt.figure(figsize=(14, 9))
    gs = GridSpec(3, 1, height_ratios=[3, 1, 2], hspace=0.05)

    ax_price = fig.add_subplot(gs[0])
    ax_volume = fig.add_subplot(gs[1], sharex=ax_price)
    ax_equity = fig.add_subplot(gs[2], sharex=ax_price)

    # ---- Add Buy/Sell markers ----
    buy_plot = mpf.make_addplot(df['Buy_marker'], type='scatter', markersize=100,
                                 marker='^', color='lime', ax=ax_price)
    sell_plot = mpf.make_addplot(df['Sell_marker'], type='scatter', markersize=100,
                                  marker='v', color='red', ax=ax_price)

    # ---- Add TA signal bands if available ----
    signal_plots = []
    if 'low' in signals.columns:
        signal_plots.append(mpf.make_addplot(signals['low'], color='tomato', linestyle='--', ax=ax_price))
    if 'mid' in signals.columns:
        signal_plots.append(mpf.make_addplot(signals['mid'], color='orange', linestyle='-', ax=ax_price))
    if 'high' in signals.columns:
        signal_plots.append(mpf.make_addplot(signals['high'], color='lightgreen', linestyle='--', ax=ax_price))

    # ---- Combine all additional plots ----
    add_plots = [buy_plot, sell_plot] + signal_plots

    # ---- Plot Candlestick and Volume ----
    mpf.plot(df,
             type='candle',
             ax=ax_price,
             volume=ax_volume,
             addplot=add_plots,
             style='nightclouds',
             xrotation=15,
             warn_too_much_data=len(df) + 1,
             show_nontrading=True)

    # ---- Plot Equity Curve ----
    if 'equity_curve' in results.columns:
        ax_equity.plot(results.index, results['equity_curve'], color='deepskyblue', label='Equity Curve')
        ax_equity.set_facecolor('#121212')
        ax_equity.tick_params(colors='white')
        ax_equity.set_ylabel("Equity", color='white')
        ax_equity.grid(True, color='#333333')
        ax_equity.legend(loc='upper left', facecolor='#121212', edgecolor='#333333', labelcolor='white')
    else:
        ax_equity.text(0.5, 0.5, 'No Equity Curve Found', transform=ax_equity.transAxes,
                       ha='center', va='center', fontsize=12, color='orange')
        ax_equity.set_axis_off()

    # ---- Final tweaks ----
    plt.setp(ax_price.get_xticklabels(), visible=False)
    plt.setp(ax_volume.get_xticklabels(), visible=False)
    fig.suptitle("Backtest Viewer: Candlesticks, Volume, Equity", color='white')

    plt.show()

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
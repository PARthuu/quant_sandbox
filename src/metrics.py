import numpy as np
import pandas as pd

def calculate_metrics(df: pd.DataFrame) -> dict:
    returns = df['strategy_return'].dropna()
    if returns.empty:
        return {'Sharpe Ratio': 0, 'Max Drawdown': 0, 'Total Return': 0}

    sharpe = np.sqrt(252) * returns.mean() / returns.std() if returns.std() != 0 else 0
    drawdown = (df['equity_curve'] / df['equity_curve'].cummax() - 1).min()
    total_return = df['equity_curve'].iloc[-1] / df['equity_curve'].iloc[0] - 1 if df['equity_curve'].iloc[0] != 0 else 0

    cagr = (df['equity_curve'].iloc[-1] / df['equity_curve'].iloc[0])**(252/len(df)) - 1 if len(df) > 0 else 0
    volatility = returns.std() * np.sqrt(252)
    win_rate = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0
    avg_gain = returns[returns > 0].mean() if not returns[returns > 0].empty else 0
    avg_loss = returns[returns < 0].mean() if not returns[returns < 0].empty else 0
    profit_factor = abs(avg_gain / avg_loss) if avg_loss != 0 else np.inf
    expectancy = returns.mean() * 100
    sortino = np.sqrt(252) * returns.mean() / returns[returns < 0].std() if not returns[returns < 0].empty else 0

    return {
        'Sharpe Ratio': round(float(sharpe), 4),
        'Sortino Ratio': round(float(sortino), 4),
        'Max Drawdown': round(float(drawdown), 4),
        'Total Return': round(float(total_return), 4),
        'CAGR': round(float(cagr), 4),
        'Volatility': round(float(volatility), 4),
        'Win Rate': round(float(win_rate), 4),
        'Avg Gain': round(float(avg_gain), 4),
        'Avg Loss': round(float(avg_loss), 4),
        'Profit Factor': round(float(profit_factor), 4),
        'Expectancy': round(float(expectancy), 4),
    }

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.data_loader import load_yfinance_data
from src.strategy import EMACrossoverStrategy, RSIStrategy, BollingerBandStrategy
from src.backtester import Backtester
from src.metrics import calculate_metrics

st.title("📊 Quant Strategy Sandbox")

strategy_options = {
    "EMA Crossover": EMACrossoverStrategy,
    "RSI": RSIStrategy,
    "Bollinger Bands": BollingerBandStrategy
}

ticker = st.text_input("Enter Ticker Symbol", value="AAPL")
start_date = st.date_input("Start Date", value=pd.to_datetime("2022-01-01"))
end_date = st.date_input("End Date", value=pd.to_datetime("2023-01-01"))
strategy_name = st.selectbox("Select Strategy", list(strategy_options.keys()))

if st.button("Run Backtest"):
    df = load_yfinance_data(ticker, start=start_date, end=end_date)

    if strategy_name == "EMA Crossover":
        short = st.slider("Short EMA Window", 5, 50, 20)
        long = st.slider("Long EMA Window", 10, 100, 50)
        strategy = EMACrossoverStrategy(df, short_window=short, long_window=long)

    elif strategy_name == "RSI":
        rsi_period = st.slider("RSI Period", 5, 30, 14)
        overbought = st.slider("Overbought Level", 50, 90, 70)
        oversold = st.slider("Oversold Level", 10, 50, 30)
        strategy = RSIStrategy(df, rsi_period=rsi_period, overbought=overbought, oversold=oversold)

    elif strategy_name == "Bollinger Bands":
        window = st.slider("BB Window", 10, 50, 20)
        std = st.slider("Standard Deviation", 1, 3, 2)
        strategy = BollingerBandStrategy(df, window=window, std_dev=std)

    signals = strategy.generate_signals()
    result_df = Backtester.run(df, signals)
    metrics = calculate_metrics(result_df)

    st.subheader("Performance Metrics")
    st.write(metrics)

    st.subheader("Equity Curve")
    fig, ax = plt.subplots()
    ax.plot(result_df['equity_curve'])
    ax.set_title("Equity Curve")
    st.pyplot(fig)

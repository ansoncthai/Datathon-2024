# process_results.py

import pandas as pd
from backtesting import Backtest
from data_validation import fetch_data, validate_and_clean_data
from indicators import (
    calculate_sma, calculate_rsi, calculate_bollinger_bands,
    calculate_macd, calculate_atr, calculate_stochastic_oscillator,
    calculate_obv, calculate_cmf, calculate_williams_r, calculate_cci,
    calculate_parabolic_sar
)
from dynamic_strategy import DynamicStrategy

def main():
    # Step 1: Fetch and Clean Data
    ticker = "AAPL"  # You can change this to any ticker you like
    start_date = "2020-01-01"
    end_date = "2023-10-01"
    df = fetch_data(ticker, start_date, end_date)
    df = validate_and_clean_data(df)

    print(df)
    if df.empty:
        print("Error: DataFrame is empty after fetching and cleaning data.")
        return

    # Make a copy of the DataFrame to avoid SettingWithCopyWarning
    df = df.copy()

    # Ensure the 'Volume' column has no NaN values (important for indicators that use Volume)
    if 'Volume' in df.columns:
        df['Volume'].fillna(method='ffill', inplace=True)  # Forward-fill missing Volume data
    else:
        print("Volume data is missing entirely in the dataset.")

    # Step 2: Calculate Technical Indicators
    df = calculate_sma(df, period=20)
    df = calculate_rsi(df, period=14)
    df = calculate_bollinger_bands(df, period=20, std_dev=2)
    df = calculate_macd(df, fast_period=12, slow_period=26, signal_period=9)
    df = calculate_atr(df, period=14)
    df = calculate_stochastic_oscillator(df, k_period=14, d_period=3)

    # Conditionally calculate OBV if Volume data is available
    if 'Volume' in df.columns and not df['Volume'].isnull().all():
        df = calculate_obv(df)
    else:
        print("Skipping OBV calculation due to missing Volume data.")

    # Continue with other indicators
    df = calculate_cmf(df, period=20)
    df = calculate_williams_r(df, period=14)
    df = calculate_cci(df, period=20)
    df = calculate_parabolic_sar(df)

    # Step 3: Set Up and Run the Backtest
    # Define conditions for the strategy
    DynamicStrategy.conditions = conditions = [
        {
            "indicator": "SMA",
            "period": 20,
            "comparison": ">",
            "reference": "Close"
        },
        {
            "indicator": "RSI",
            "period": 14,
            "comparison": "<",
            "value": 70
        },
        # Add more conditions as needed
    ]

    bt = Backtest(
        df,
        DynamicStrategy,
        cash=10000,
        commission=0.002,
        trade_on_close=True
    )
    stats = bt.run()

    # Step 4: Process and Display Results
    print(stats)
    bt.plot()

if __name__ == "__main__":
    main()
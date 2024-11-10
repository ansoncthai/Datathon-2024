from flask import Flask, request, jsonify
from backtesting import Backtest
import pandas as pd
from dynamic_strategy import DynamicStrategy
from data_validation import fetch_data, validate_and_clean_data

# Import indicator calculation functions
from indicators import (
    calculate_sma,
    calculate_rsi,
    calculate_bollinger_bands,
    calculate_macd,
    calculate_atr,
    calculate_stochastic_oscillator,
    calculate_obv,
    calculate_cmf,
    calculate_williams_r,
    calculate_cci,
    calculate_donchian_channels,
    calculate_parabolic_sar
)

app = Flask(__name__)

def add_indicators(df, params):
    """Apply necessary indicators to the DataFrame based on user parameters."""
    for condition in params.get("conditions", []):
        indicator = condition.get("indicator")
        period = condition.get("period", 14)  # default period
        value = condition.get("value", 2)  # for Bollinger Bands std_dev, etc.

        if indicator == "SMA":
            df = calculate_sma(df, period)
        elif indicator == "RSI":
            df = calculate_rsi(df, period)
        elif indicator == "Bollinger Bands":
            df = calculate_bollinger_bands(df, period, std_dev=value)
        elif indicator == "MACD":
            df = calculate_macd(df, fast_period=12, slow_period=26, signal_period=9)
        elif indicator == "ATR":
            df = calculate_atr(df, period)
        elif indicator == "Stochastic Oscillator":
            df = calculate_stochastic_oscillator(df, k_period=14, d_period=3)
        elif indicator == "OBV":
            df = calculate_obv(df)
        elif indicator == "CMF":
            df = calculate_cmf(df, period)
        elif indicator == "Williams %R":
            df = calculate_williams_r(df, period)
        elif indicator == "CCI":
            df = calculate_cci(df, period)
        elif indicator == "Donchian Channels":
            df = calculate_donchian_channels(df, period)
        elif indicator == "Parabolic SAR":
            df = calculate_parabolic_sar(df)
    return df

@app.route('/api/run-backtest', methods=['POST'])
def run_backtest():
    data = request.json

    # Step 1: Fetch and validate historical data
    try:
        df = fetch_data(data['ticker'], data['start_date'], data['end_date'])
        
        # Flatten MultiIndex if necessary
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Rename columns to match expected format
        column_mapping = {
            'Adj Close': 'Close',
            'close': 'Close',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'volume': 'Volume'
        }
        df.rename(columns=column_mapping, inplace=True)

        # Validate essential columns
        required_columns = {'Open', 'High', 'Low', 'Close'}
        if not required_columns.issubset(df.columns):
            return jsonify({"error": "DataFrame must include 'Open', 'High', 'Low', and 'Close' columns"}), 400

        # Validate and clean data
        df = validate_and_clean_data(df)

        # Step 2: Add indicators based on user-defined parameters
        df = add_indicators(df, data['params'])

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Step 3: Set up parameters within the strategy
    params = data['params']
    DynamicStrategy.params = params  # Set params as a class variable

    # Step 4: Run the backtest with `backtesting.py`
    bt = Backtest(df, DynamicStrategy, cash=10000, commission=.002)
    stats = bt.run()

    # Step 5: Safely access 'Max Drawdown [%]' if available
    max_drawdown = stats.get('Max Drawdown [%]', "N/A")

    # Step 6: Process 'trade_history' to convert Timedelta columns
    if '_trades' in dir(stats):
        trades_df = stats._trades.copy()
        # Convert Timedelta columns to total seconds or strings
        timedelta_cols = trades_df.select_dtypes(include=['timedelta64[ns]', 'timedelta64']).columns
        for col in timedelta_cols:
            trades_df[col] = trades_df[col].dt.total_seconds()  # or trades_df[col].astype(str)
        trade_history = trades_df.to_dict(orient="records")
    else:
        trade_history = []

    # Step 7: Return the results to the frontend
    return jsonify({
        "total_return": stats.get('Return [%]', "N/A"),
        "max_drawdown": max_drawdown,
        "trade_history": trade_history
    })

if __name__ == '__main__':
    app.run(debug=True)

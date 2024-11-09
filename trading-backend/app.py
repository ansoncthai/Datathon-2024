from flask import Flask, request, jsonify
from backtesting import Backtest
import pandas as pd
from dynamic_strategy import DynamicStrategy
from data_validation import fetch_data, validate_and_clean_data

app = Flask(__name__)

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

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Step 2: Set up parameters within the strategy
    params = data['params']
    DynamicStrategy.params = params  # Set params as a class variable

    # Step 3: Run the backtest with `backtesting.py`
    bt = Backtest(df, DynamicStrategy, cash=10000, commission=.002)
    stats = bt.run()

    # Step 4: Safely access 'Max Drawdown [%]' if available
    max_drawdown = stats.get('Max Drawdown [%]', "N/A")  # Provide a default if the key does not exist

    # Step 5: Process 'trade_history' to convert Timedelta columns
    if '_trades' in dir(stats):
        trades_df = stats._trades.copy()
        # Convert Timedelta columns to total seconds or strings
        timedelta_cols = trades_df.select_dtypes(include=['timedelta64[ns]', 'timedelta64']).columns
        for col in timedelta_cols:
            trades_df[col] = trades_df[col].dt.total_seconds()  # or trades_df[col].astype(str)
        trade_history = trades_df.to_dict(orient="records")
    else:
        trade_history = []

    # Step 6: Return the results to the frontend
    return jsonify({
        "total_return": stats.get('Return [%]', "N/A"),
        "max_drawdown": max_drawdown,
        "trade_history": trade_history
    })

if __name__ == '__main__':
    app.run(debug=True)

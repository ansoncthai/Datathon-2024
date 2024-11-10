import pandas as pd
from flask import Flask, request, jsonify
from backtesting import Backtest
import numpy as np
from dynamic_strategy import DynamicStrategy
from data_validation import fetch_data, validate_and_clean_data
from indicators import calculate_indicators

app = Flask(__name__)

@app.route('/api/run-backtest', methods=['POST'])
def run_backtest():
    data = request.json
    print("Received data:", data)

    # Step 1: Fetch and validate historical data
    try:
        df = fetch_data(data['ticker'], data['start_date'], data['end_date'])
        
        # Flatten MultiIndex if necessary
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Prioritize 'Adj Close' over 'Close'
        if 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']
            df.drop(columns=['Adj Close'], inplace=True)
        
        # Rename columns to match expected format
        column_mapping = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'volume': 'Volume',
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Volume': 'Volume',
        }
        df.rename(columns=column_mapping, inplace=True)
        
        # Validate essential columns
        required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
        if not required_columns.issubset(df.columns):
            return jsonify({"error": f"DataFrame must include {required_columns} columns"}), 400

        # Validate and clean data
        df = validate_and_clean_data(df)

        print(f"Data after validation: {len(df)} rows")
        print(df.head())

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Step 2: Calculate Required Indicators
    try:
        # Collect all required indicators from conditions and exits
        required_indicators = []
        for condition in data['params'].get('conditions', []) + data['params'].get('exits', []):
            required_indicators.append(condition)

        # Calculate only the required indicators
        df = calculate_indicators(df, required_indicators)
        print("DataFrame columns after indicator calculations:", df.columns)
        print(df.head())
        
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return jsonify({"error": f"Error calculating indicators: {e}"}), 400

    print(f"Data after indicator calculations: {len(df)} rows")

    # Step 3: Handle NaNs
    essential_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df.dropna(subset=essential_columns, inplace=True)
    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)

    print(f"Data after handling NaNs: {len(df)} rows")

    if df.empty:
        return jsonify({"error": "No data available after processing. Please adjust your date range or check your indicators."}), 400

    # Step 4: Assign params to DynamicStrategy
    print("Assigning parameters to DynamicStrategy:", data.get("params", {}))
    DynamicStrategy.params = data.get("params", {})

    # Step 5: Run the backtest with provided initial_cash and commission
    try:
        initial_cash = data.get('initial_cash', 10000)
        commission = data.get('commission', 0.002)
        print(f"Running backtest with initial_cash={initial_cash}, commission={commission}")
        bt = Backtest(df, DynamicStrategy, cash=initial_cash, commission=commission)
        # bt = Backtest(df, DynamicStrategy, cash=initial_cash, commission=commission, trade_on_close=True)
        stats = bt.run()
    except KeyError as e:
        print(f"Missing column in data: {e}")
        return jsonify({"error": f"Missing column in data: {e}"}), 400
    except Exception as e:
        print(f"Error during backtesting: {e}")
        return jsonify({"error": f"Error during backtesting: {e}"}), 400

    # Step 6: Collect relevant performance metrics
    total_return = stats.get('Return [%]', "N/A")
    max_drawdown = stats.get('Max Drawdown [%]', "N/A")
    win_rate = stats.get('Win Rate [%]', "N/A")
    profit_factor = stats.get('Profit Factor', "N/A")
    sharpe_ratio = stats.get('Sharpe Ratio', "N/A")

    if pd.isna(profit_factor) or np.isinf(profit_factor):
        profit_factor = "Infinity" if np.isinf(profit_factor) else "N/A"

    # Step 7: Process trade history to prepare it for the frontend
    trade_history = []
    if '_trades' in dir(stats):
        trades_df = stats._trades.copy()
        timedelta_cols = trades_df.select_dtypes(include=['timedelta64[ns]', 'timedelta64']).columns
        for col in timedelta_cols:
            trades_df[col] = trades_df[col].dt.total_seconds()
        trade_history = trades_df.to_dict(orient="records")

    # Step 8: Format results for frontend
    results = {
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "sharpe_ratio": sharpe_ratio,
        "trade_history": trade_history
    }

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

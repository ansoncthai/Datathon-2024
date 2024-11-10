import pandas as pd
from flask import Flask, request, jsonify
from backtesting import Backtest
from dynamic_strategy import DynamicStrategy
from data_validation import fetch_data, validate_and_clean_data
from indicators import (
    calculate_sma, calculate_rsi, calculate_bollinger_bands, calculate_macd,
    calculate_atr, calculate_stochastic_oscillator, calculate_obv,
    calculate_cmf, calculate_williams_r, calculate_cci,
    calculate_donchian_channels, calculate_parabolic_sar
)

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

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Step 2: Calculate Indicators
    try:
        df = calculate_sma(df, data['params']['sma_long'])
        df = calculate_rsi(df, data['params']['rsi_period'])
        df = calculate_bollinger_bands(df, data['params']['bollinger_period'], data['params']['bollinger_std_dev'])
        df = calculate_macd(df, data['params']['macd_fast'], data['params']['macd_slow'], data['params']['macd_signal'])
        df = calculate_atr(df, data['params']['atr_period'])
        df = calculate_stochastic_oscillator(df, data['params']['stochastic_period'], data['params']['stochastic_smooth'])
        df = calculate_obv(df)
        df = calculate_cmf(df, data['params']['cmf_period'])
        df = calculate_williams_r(df, data['params']['williams_r_period'])
        df = calculate_cci(df, data['params']['cci_period'])
        df = calculate_donchian_channels(df, data['params']['donchian_period'])
        df = calculate_parabolic_sar(df, data['params']['parabolic_sar_af'], data['params']['parabolic_sar_max_af'])
    except Exception as e:
        return jsonify({"error": f"Error calculating indicators: {e}"}), 400

    # Handle NaNs by forward/backward filling and ensuring non-essential columns don’t interfere
    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)

    # Step 3: Define parameters for the backtest
    params = {
        "conditions": [
            {"indicator": "RSI", "period": data['params']['rsi_period'], "comparison": "<", "value": 30},
            {"indicator": "SMA", "period": data['params']['sma_long'], "comparison": ">", "reference": "Close"}
        ]
    }
    DynamicStrategy.params = params

    # Step 4: Run the backtest
    try:
        bt = Backtest(df, DynamicStrategy, cash=10000, commission=0.002)
        stats = bt.run()
    except Exception as e:
        return jsonify({"error": f"Error during backtesting: {e}"}), 400

    # Step 5: Collect relevant performance metrics
    total_return = stats.get('Return [%]', "N/A")
    max_drawdown = stats.get('Max Drawdown [%]', 0.0)
    win_rate = stats.get('Win Rate [%]', 0.0)
    profit_factor = stats.get('Profit Factor', 1.0)
    sharpe_ratio = stats.get('Sharpe Ratio', "N/A")

    # Step 6: Process trade history to prepare it for the frontend
    trade_history = []
    if '_trades' in dir(stats):
        trades_df = stats._trades.copy()
        timedelta_cols = trades_df.select_dtypes(include=['timedelta64[ns]', 'timedelta64']).columns
        for col in timedelta_cols:
            trades_df[col] = trades_df[col].dt.total_seconds()
        trade_history = trades_df.to_dict(orient="records")

    # Step 7: Format results for frontend
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

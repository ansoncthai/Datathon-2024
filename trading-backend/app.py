from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from ta import add_all_ta_features  # or use TA-Lib if available
from backtesting import Backtest, Strategy  # Use if needed for backtesting
import yfinance as yf  # Fetch data

app = Flask(__name__)

@app.route('/api/data', methods=['POST'])
def get_data():
    data = request.json
    # Process your data or run backtest here
    # Example: Fetch data from yfinance
    df = yf.download(data['ticker'], start=data['start'], end=data['end'])
    
    # Preprocess and send back results
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    return jsonify(df.to_dict(orient='records'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

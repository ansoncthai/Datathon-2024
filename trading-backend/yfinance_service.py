import yfinance as yf
import backtrader as bt
import pandas as pd

# Step 1: Fetch historical data
ticker = "AAPL"
start_date = "2020-01-01"
end_date = "2021-01-01"
data = yf.download(ticker, start=start_date, end=end_date, group_by='column')

# Select only the first level of each column and convert to lowercase
data.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in data.columns]
print(data.columns)

# Step 3: Handle any NaN values
data.fillna(method='ffill', inplace=True)  # Forward fill any NaNs
data.dropna(inplace=True)  # Drop rows that still have NaNs after forward filling

# Verify the cleaned data
print("Column names:", data.columns)
print("Checking for NaNs:\n", data.isnull().sum())  # Should show 0 for all columns

# Step 4: Define a simple Moving Average Crossover Strategy
class SmaCross(bt.Strategy):
    params = (("fast_period", 10), ("slow_period", 30),)

    def __init__(self):
        # Define the moving averages
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)

    def next(self):
        # Print the current close price for debugging purposes
        print(f"Current Close Price: {self.data.close[0]}")
        
        if not self.position:  # Not in a position
            if self.fast_ma > self.slow_ma:  # Golden cross
                self.buy()
        elif self.fast_ma < self.slow_ma:  # Death cross
            self.close()

# Step 5: Initialize the Backtrader engine (Cerebro)
cerebro = bt.Cerebro()

# Step 6: Convert the yfinance data to a format Backtrader can use
data_bt = bt.feeds.PandasData(dataname=data)

# Step 7: Add the data feed and strategy
cerebro.adddata(data_bt)
cerebro.addstrategy(SmaCross)
cerebro.broker.setcash(10000)

# Step 8: Add analyzers to assess strategy performance
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trade_analyzer")  # Win Rate, Profit Factor
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")  # Sharpe Ratio
cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")  # Max Drawdown

# Step 9: Run the backtest
print("Starting Portfolio Value:", cerebro.broker.getvalue())
results = cerebro.run()
strategy_results = results[0]
print("Final Portfolio Value:", cerebro.broker.getvalue())

# Step 10: Retrieve and print analyzer metrics
trade_analysis = strategy_results.analyzers.trade_analyzer.get_analysis()
sharpe_ratio = strategy_results.analyzers.sharpe.get_analysis()
drawdown = strategy_results.analyzers.drawdown.get_analysis()

# Calculate Win Rate and Profit Factor
win_rate = trade_analysis.won.total / trade_analysis.total.closed if trade_analysis.total.closed else 0
profit_factor = (trade_analysis.won.pnl.total / abs(trade_analysis.lost.pnl.total)
                 if trade_analysis.lost.pnl.total else "N/A")

# Display metrics
print("\nStrategy Performance Metrics:")
print("Win Rate:", win_rate * 100, "%")
print("Profit Factor:", profit_factor)
print("Sharpe Ratio:", sharpe_ratio.get('sharperatio', 'Data not available'))
print("Max Drawdown (%):", drawdown.max.drawdown)

# Safely access 'money' attribute
max_drawdown_value = drawdown.max.get('money', None)
if max_drawdown_value is not None:
    print("Max Drawdown (Value):", max_drawdown_value)
else:
    print("Max Drawdown (Value): Data not available")

# Optionally, print other available attributes
print("\nOther available drawdown metrics:")
for key, value in drawdown.max.items():
    print(f"{key}: {value}")

# Step 11: Plot the results if no errors with portfolio value
try:
    cerebro.plot()
except ValueError as e:
    print(f"Plotting error: {e}")
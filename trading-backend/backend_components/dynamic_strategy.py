from backtesting import Strategy
from backtesting.lib import crossover
from backtesting.test import SMA  
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.trend import MACD
import pandas as pd

class DynamicStrategy(Strategy):
    params = {}  # Class variable to hold params

    def init(self):
        # Access parameters as self.params
        self.params = self.__class__.params

        # Ensure self.data.Close is a pandas Series for compatibility with ta library indicators
        close_series = pd.Series(self.data.Close) if not isinstance(self.data.Close, pd.Series) else self.data.Close

        # Initialize indicators based on user parameters

        # 1. SMA (Simple Moving Average)
        if 'sma_period' in self.params:
            self.sma = self.I(SMA, close_series, self.params['sma_period'])

        # 2. RSI (Relative Strength Index)
        if 'rsi_period' in self.params:
            self.rsi = RSIIndicator(close=close_series, window=self.params['rsi_period'])
            self.rsi_values = self.I(lambda: self.rsi.rsi())
            self.rsi_overbought = self.params.get('rsi_overbought', 70)
            self.rsi_oversold = self.params.get('rsi_oversold', 30)

        # 3. Bollinger Bands
        if 'bollinger_period' in self.params and 'bollinger_std_dev' in self.params:
            bb = BollingerBands(close=close_series, window=self.params['bollinger_period'], window_dev=self.params['bollinger_std_dev'])
            self.bollinger_upper = self.I(lambda: bb.bollinger_hband())
            self.bollinger_lower = self.I(lambda: bb.bollinger_lband())

        # 4. MACD (Moving Average Convergence Divergence)
        if 'macd_fast' in self.params and 'macd_slow' in self.params and 'macd_signal' in self.params:
            macd = MACD(close=close_series, window_slow=self.params['macd_slow'], window_fast=self.params['macd_fast'], window_sign=self.params['macd_signal'])
            self.macd_line = self.I(lambda: macd.macd())
            self.macd_signal_line = self.I(lambda: macd.macd_signal())

        # 5. ATR (Average True Range)
        if 'atr_period' in self.params:
            atr = AverageTrueRange(high=self.data.High, low=self.data.Low, close=close_series, window=self.params['atr_period'])
            self.atr = self.I(lambda: atr.average_true_range())

    def next(self):
        """
        Define trading rules based on indicators.
        Example: SMA crossover, RSI overbought/oversold, Bollinger Band mean reversion, MACD crossover.
        """
        
        # Example Rule 1: SMA Crossover (if both short and long SMAs are defined)
        if hasattr(self, 'sma') and hasattr(self, 'macd_line'):
            if crossover(self.sma, self.macd_line):  # Example logic for crossover
                self.buy()
            elif crossover(self.macd_line, self.sma):
                self.sell()
        
        # Example Rule 2: RSI Overbought/Oversold
        if hasattr(self, 'rsi_values'):
            if self.rsi_values[-1] < self.rsi_oversold:
                self.buy()
            elif self.rsi_values[-1] > self.rsi_overbought:
                self.sell()
        
        # Example Rule 3: Bollinger Bands Mean Reversion
        if hasattr(self, 'bollinger_upper') and hasattr(self, 'bollinger_lower'):
            if self.data.Close[-1] > self.bollinger_upper[-1]:
                self.sell()
            elif self.data.Close[-1] < self.bollinger_lower[-1]:
                self.buy()
        
        # Example Rule 4: MACD Line Crossover
        if hasattr(self, 'macd_line') and hasattr(self, 'macd_signal_line'):
            if crossover(self.macd_line, self.macd_signal_line):
                self.buy()
            elif crossover(self.macd_signal_line, self.macd_line):
                self.sell()

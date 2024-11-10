import pandas as pd
import pandas_ta as ta

def calculate_sma(df, period):
    """Simple Moving Average (SMA)"""
    df[f"SMA_{period}"] = ta.sma(df['Close'], length=period)
    return df

def calculate_rsi(df, period, overbought=70, oversold=30):
    """Relative Strength Index (RSI)"""
    df[f"RSI_{period}"] = ta.rsi(df['Close'], length=period)
    df['RSI_Overbought'] = overbought
    df['RSI_Oversold'] = oversold
    return df

def calculate_bollinger_bands(df, period, std_dev):
    """Bollinger Bands"""
    bb = ta.bbands(df['Close'], length=period, std=std_dev)
    df = pd.concat([df, bb], axis=1)
    return df

def calculate_macd(df, fast_period, slow_period, signal_period):
    """Moving Average Convergence Divergence (MACD)"""
    macd = ta.macd(df['Close'], fast=fast_period, slow=slow_period, signal=signal_period)
    df = pd.concat([df, macd], axis=1)
    return df

def calculate_atr(df, period):
    """Average True Range (ATR)"""
    df[f"ATR_{period}"] = ta.atr(df['High'], df['Low'], df['Close'], length=period)
    return df

def calculate_stochastic_oscillator(df, k_period, d_period):
    """Stochastic Oscillator"""
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=k_period, d=d_period)
    df = pd.concat([df, stoch], axis=1)
    return df

def calculate_obv(df):
    """On-Balance Volume (OBV)"""
    # Check if 'Close' and 'Volume' columns exist
    if 'Close' not in df.columns or 'Volume' not in df.columns:
        raise ValueError("DataFrame must contain 'Close' and 'Volume' columns for OBV calculation.")

    # Drop rows with missing values in 'Close' or 'Volume'
    df = df.dropna(subset=['Close', 'Volume'])

    # Calculate OBV
    obv = ta.obv(df['Close'], df['Volume'])
    df["OBV"] = obv
    return df

def calculate_cmf(df, period):
    """Chaikin Money Flow (CMF)"""
    df[f"CMF_{period}"] = ta.cmf(df['High'], df['Low'], df['Close'], df['Volume'], length=period)
    return df

def calculate_williams_r(df, period):
    """Williams %R"""
    df[f"Williams_%R_{period}"] = ta.willr(df['High'], df['Low'], df['Close'], length=period)
    return df

def calculate_cci(df, period):
    """Commodity Channel Index (CCI)"""
    df[f"CCI_{period}"] = ta.cci(df['High'], df['Low'], df['Close'], length=period)
    return df

def calculate_donchian_channels(df, period):
    """Donchian Channels"""
    dc = ta.donchian(df['High'], df['Low'], lower_length=period, upper_length=period)
    df = pd.concat([df, dc], axis=1)
    return df

def calculate_parabolic_sar(df, af=0.02, max_af=0.2):
    """Parabolic SAR"""
    psar = ta.psar(df['High'], df['Low'], df['Close'], af=af, max_af=max_af)
    df = pd.concat([df, psar], axis=1)  # Concatenate the multiple columns returned by psar
    df.dropna(inplace=True)  # Drop 
import pandas as pd
import pandas_ta as ta

def calculate_indicators(df, conditions):
    """Calculates only the indicators required by the conditions and exits."""
    calculated_indicators = set()
    for condition in conditions:
        # Main indicator
        indicator = condition.get("indicator")
        period = condition.get("period", 14)  # Default period if not specified

        # Check if the main indicator is already calculated
        indicator_column = get_indicator_column_name(indicator, period)
        if indicator_column not in df.columns and indicator_column not in calculated_indicators:
            df = calculate_indicator(df, indicator, period)
            calculated_indicators.add(indicator_column)

        # Reference indicator
        reference = condition.get("reference", None)
        if reference:
            # Extract indicator and period from reference (e.g., 'SMA_50')
            ref_parts = reference.split('_')
            if len(ref_parts) == 2:
                ref_indicator = ref_parts[0]
                ref_period = int(ref_parts[1])

                # Check if the reference indicator is already calculated
                ref_indicator_column = get_indicator_column_name(ref_indicator, ref_period)
                if ref_indicator_column not in df.columns and ref_indicator_column not in calculated_indicators:
                    df = calculate_indicator(df, ref_indicator, ref_period)
                    calculated_indicators.add(ref_indicator_column)
            else:
                raise ValueError(f"Invalid reference format: {reference}")

    return df

def calculate_indicator(df, indicator, period):
    """Calculates the specified indicator and adds it to the DataFrame."""
    if indicator == "SMA":
        df = calculate_sma(df, period)
    elif indicator == "EMA":
        df = calculate_ema(df, period)
    elif indicator == "RSI":
        df = calculate_rsi(df, period)
    elif indicator == "ATR":
        df = calculate_atr(df, period)
    elif indicator == "CCI":
        df = calculate_cci(df, period)
    elif indicator == "CMF":
        df = calculate_cmf(df, period)
    elif indicator == "Williams %R":
        df = calculate_williams_r(df, period)
    elif indicator == "Donchian Channels":
        df = calculate_donchian_channels(df, period)
    elif indicator == "Parabolic SAR":
        df = calculate_parabolic_sar(df)
    elif indicator == "MACD":
        df = calculate_macd(df, 12, 26, 9)
    else:
        raise ValueError(f"Indicator {indicator} not supported.")
    return df


def get_indicator_column_name(indicator, period):
    """Maps indicator names to DataFrame column names."""
    indicator_mapping = {
        "RSI": f"RSI_{period}",
        "SMA": f"SMA_{period}",
        "EMA": f"EMA_{period}",
        "ATR": f"ATR_{period}",
        "CCI": f"CCI_{period}",
        "CMF": f"CMF_{period}",
        "Williams %R": f"Williams_%R_{period}",
        "Donchian Channels": [f"DCL_{period}", f"DCU_{period}"],  # Lower and Upper bands
        "Parabolic SAR": ["PSARl_0.02_0.2", "PSARs_0.02_0.2"],  # Long and Short PSAR
        "MACD": ["MACD_12_26_9", "MACDh_12_26_9", "MACDs_12_26_9"],  # MACD columns
        # Add more mappings as needed
    }
    return indicator_mapping.get(indicator)

# Existing indicator calculation functions
def calculate_sma(df, period):
    """Simple Moving Average (SMA)"""
    df[f"SMA_{period}"] = ta.sma(df['Close'], length=period)
    return df

def calculate_ema(df, period):
    """Exponential Moving Average (EMA)"""
    df[f"EMA_{period}"] = ta.ema(df['Close'], length=period)
    return df

def calculate_rsi(df, period, overbought=70, oversold=30):
    """Relative Strength Index (RSI)"""
    df[f"RSI_{period}"] = ta.rsi(df['Close'], length=period)
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
    df = pd.concat([df, psar], axis=1)
    df.dropna(inplace=True)
    return df  # Add this line to return the DataFrame

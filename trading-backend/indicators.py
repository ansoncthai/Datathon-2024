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
        indicator_columns = get_indicator_column_name(indicator, period)
        if not indicator_columns:
            raise ValueError(f"Indicator {indicator} not recognized.")

        if isinstance(indicator_columns, list):
            missing_columns = [col for col in indicator_columns if col not in df.columns and col not in calculated_indicators]
            if missing_columns:
                print(f"Calculating indicator: {indicator} with period: {period}")
                df = calculate_indicator(df, indicator, period)
                calculated_indicators.update(indicator_columns)
        else:
            if indicator_columns not in df.columns and indicator_columns not in calculated_indicators:
                print(f"Calculating indicator: {indicator} with period: {period}")
                df = calculate_indicator(df, indicator, period)
                calculated_indicators.add(indicator_columns)

        # Reference indicator
        reference = condition.get("reference", None)
        if reference:
            # Extract indicator and period from reference (e.g., 'SMA_50')
            ref_parts = reference.split('_')
            if len(ref_parts) == 2:
                ref_indicator = ref_parts[0]
                ref_period = int(ref_parts[1])

                # Check if the reference indicator is already calculated
                ref_indicator_columns = get_indicator_column_name(ref_indicator, ref_period)
                if not ref_indicator_columns:
                    raise ValueError(f"Reference indicator {ref_indicator} not recognized.")

                if isinstance(ref_indicator_columns, list):
                    missing_ref_columns = [col for col in ref_indicator_columns if col not in df.columns and col not in calculated_indicators]
                    if missing_ref_columns:
                        print(f"Calculating reference indicator: {ref_indicator} with period: {ref_period}")
                        df = calculate_indicator(df, ref_indicator, ref_period)
                        calculated_indicators.update(ref_indicator_columns)
                else:
                    if ref_indicator_columns not in df.columns and ref_indicator_columns not in calculated_indicators:
                        print(f"Calculating reference indicator: {ref_indicator} with period: {ref_period}")
                        df = calculate_indicator(df, ref_indicator, ref_period)
                        calculated_indicators.add(ref_indicator_columns)
            else:
                raise ValueError(f"Invalid reference format: {reference}")

    return df

def calculate_indicator(df, indicator, period):
    """Calculates the specified indicator and adds it to the DataFrame."""
    print(f"Calculating indicator: {indicator} with period: {period}")
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
        "Donchian Channels": f"DCL_{period}",  # Lower band
        "Parabolic SAR": "PSAR_0.02_0.2",      # Default PSAR column
        "MACD": f"MACD_12_26_9",               # MACD line
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

def calculate_rsi(df, period):
    """Relative Strength Index (RSI)"""
    df[f"RSI_{period}"] = ta.rsi(df['Close'], length=period)
    return df

# def calculate_macd(df, fast_period, slow_period, signal_period):
#     """Moving Average Convergence Divergence (MACD)"""
#     macd = ta.macd(df['Close'], fast=fast_period, slow=slow_period, signal=signal_period)
#     df = pd.concat([df, macd], axis=1)
#     return df
def calculate_macd(df, fast_period, slow_period, signal_period):
    """Moving Average Convergence Divergence (MACD)"""
    # Calculate MACD line only (you can specify which line to return)
    macd = ta.macd(df['Close'], fast=fast_period, slow=slow_period, signal=signal_period)['MACD_12_26_9']
    df['MACD_12_26_9'] = macd  # Only add the MACD line to the DataFrame
    return df

def calculate_atr(df, period):
    """Average True Range (ATR)"""
    df[f"ATR_{period}"] = ta.atr(df['High'], df['Low'], df['Close'], length=period)
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

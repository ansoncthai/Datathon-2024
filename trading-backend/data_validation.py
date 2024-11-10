import yfinance as yf

def fetch_data(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        raise ValueError(f"No data found for ticker '{ticker}' between {start_date} and {end_date}.")
    return df

def validate_and_clean_data(df):
    required_columns = ['Close', 'Volume', 'Open', 'High', 'Low']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"DataFrame is missing required column: {col}")
    df = df.dropna(subset=required_columns)  # Remove rows with NaNs in essential columns
    return df

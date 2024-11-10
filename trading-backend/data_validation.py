# data_validation.py
import yfinance as yf

def fetch_data(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date)
    return df

def validate_and_clean_data(df):

    # Select only the first level of each column and convert to lowercase
    # df.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in df.columns]
    df.columns = [col[0] if isinstance(col, tuple) else col.lower() for col in df.columns]

    df.ffill(inplace=True)  # Replace deprecated fillna(method='ffill')
    df = df.asfreq('D').ffill()  # Replace deprecated fillna(method='ffill') in asfreq()
    return df

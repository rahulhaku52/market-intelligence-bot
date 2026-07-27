import pandas as pd

def clean_historical(df):
    if df is None or df.empty:
        return None
    df = df.dropna()
    return df

def clean_info(info):
    if info is None:
        return {}
    keys = ['previousClose', 'open', 'dayLow', 'dayHigh', 'volume', 'marketCap',
            'trailingPE', 'forwardPE', 'returnOnEquity', 'debtToEquity',
            'revenueGrowth', 'earningsGrowth', 'dividendRate']
    return {k: info.get(k) for k in keys}

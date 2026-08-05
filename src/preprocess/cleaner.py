def clean_historical(df):
    return df.dropna() if df is not None and not df.empty else None

def clean_info(info):
    if not info: return {}
    needed = ['previousClose','open','dayLow','dayHigh','volume','marketCap','trailingPE','forwardPE',
              'returnOnEquity','debtToEquity','revenueGrowth','earningsGrowth','dividendRate',
              'fiftyTwoWeekLow','fiftyTwoWeekHigh','bookValue','priceToBook','pegRatio']
    return {k: info.get(k) for k in needed}
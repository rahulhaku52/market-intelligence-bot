import os, finnhub
def get_client():
    return finnhub.Client(api_key=os.environ['FINNHUB_API_KEY'])
def fetch_news(ticker, from_date, to_date):
    return get_client().company_news(ticker, _from=from_date, to=to_date)
def fetch_quote(ticker):
    return get_client().quote(ticker)
def fetch_financials(ticker):
    # Finnhub free tier doesn't have full financials, we use yahoo for that
    return {}
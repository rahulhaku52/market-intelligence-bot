import os
import finnhub
from src.utils.logger import logger

def get_client():
    key = os.environ.get('FINNHUB_API_KEY')
    if not key:
        logger.warning("FINNHUB_API_KEY not set")
        return None
    return finnhub.Client(api_key=key)

def fetch_quote(ticker):
    client = get_client()
    if not client:
        return None
    try:
        return client.quote(ticker)
    except Exception as e:
        logger.warning(f"Finnhub quote failed for {ticker}: {e}")
        return None

def fetch_news(ticker, from_date, to_date):
    client = get_client()
    if not client:
        return []
    try:
        return client.company_news(ticker, _from=from_date, to=to_date)
    except Exception as e:
        logger.warning(f"Finnhub news failed for {ticker}: {e}")
        return []

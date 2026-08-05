import time
from tenacity import retry, stop_after_attempt, wait_exponential
import requests_cache
from functools import lru_cache

# Enable caching for HTTP requests (24 hours TTL)
requests_cache.install_cache('api_cache', expire_after=86400)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def safe_fetch(func, *args, **kwargs):
    return func(*args, **kwargs)

def fallback_yahoo(ticker):
    # if yfinance fails, try finnhub
    from .finnhub import fetch_quote
    return fetch_quote(ticker)
import yfinance as yf

def fetch_yahoo(ticker, period="1mo"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except Exception as e:
        print(f"Yahoo error for {ticker}: {e}")
        return None, None

import yfinance as yf

def fetch(ticker, period="1mo", interval="1d"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    info = stock.info
    return hist, info

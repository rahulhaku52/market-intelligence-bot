import yfinance as yf
def fetch(ticker, period="3mo"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    info = stock.info
    return hist, info
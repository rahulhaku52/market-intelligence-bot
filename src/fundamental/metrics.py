def extract_fundamentals(info):
    # info comes from yfinance
    return {
        'PE': info.get('trailingPE'),
        'Forward PE': info.get('forwardPE'),
        'EPS': info.get('trailingEps'),
        'ROE': info.get('returnOnEquity'),
        'ROCE': None,  # not directly in yfinance
        'Debt/Equity': info.get('debtToEquity'),
        'Revenue Growth': info.get('revenueGrowth'),
        'Earnings Growth': info.get('earningsGrowth'),
        'Dividend Yield': info.get('dividendRate'),
        'Promoter Holding': None,  # yfinance doesn't have
        'Book Value': info.get('bookValue'),
        'P/B': info.get('priceToBook'),
        'PEG': info.get('pegRatio')
    }
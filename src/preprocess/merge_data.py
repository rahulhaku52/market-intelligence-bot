def merge_data(ticker, yahoo_hist, yahoo_info, finnhub_quote, news_articles, finnhub_news):
    return {
        'ticker': ticker,
        'historical': yahoo_hist.to_dict('records') if yahoo_hist is not None else [],
        'info': yahoo_info,
        'quote': finnhub_quote,
        'news_articles': news_articles,
        'finnhub_news': finnhub_news,
    }

def merge(ticker, y_hist, y_info, f_quote, news_articles, f_news):
    return {
        'ticker': ticker,
        'history': y_hist.to_dict('records') if y_hist is not None else [],
        'info': y_info,
        'quote': f_quote,
        'news_articles': news_articles,
        'finnhub_news': f_news
    }
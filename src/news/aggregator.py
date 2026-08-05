from datetime import date, timedelta
from src.fetchers.finnhub import fetch_news as fetch_finnhub_news
from src.fetchers.newsapi import fetch_news as fetch_newsapi_news
from src.news_enhanced.dedup import remove_duplicates
from src.news_enhanced.source_weight import weight_articles
from src.news_enhanced.event_classifier import classify_event
from src.sentiment.news_score import score_articles

def aggregate_and_score_news(ticker: str) -> dict:
    today = date.today()
    from_date = (today - timedelta(days=2)).isoformat()
    to_date = today.isoformat()
    
    clean_ticker = ticker.replace('.NS', '')
    
    f_news = fetch_finnhub_news(ticker, from_date, to_date)
    n_articles = fetch_newsapi_news(clean_ticker, from_date, to_date)
    
    # Convert finnhub format to standard article list
    formatted_finnhub = [{'title': a.get('headline', ''), 'description': a.get('summary', ''), 'source': {'name': 'Finnhub'}} for a in f_news]
    
    all_articles = n_articles + formatted_finnhub
    if not all_articles:
        return {'score': None, 'articles_count': 0, 'top_event': 'NONE'}
        
    deduped = remove_duplicates(all_articles)
    weighted = weight_articles(deduped)
    
    sentiment_raw = score_articles(weighted)  # -30 to +30
    sentiment_score = int((sentiment_raw + 30) / 60.0 * 100.0)
    
    top_event = classify_event(weighted[0]) if weighted else 'GENERAL'
    
    return {
        'score': sentiment_score,
        'articles_count': len(weighted),
        'top_event': top_event
    }

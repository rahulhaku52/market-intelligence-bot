import argparse
import os
import sys
from datetime import date, timedelta, datetime
from src.utils.config_loader import get_categories
from src.database.supabase_client import get_supabase
from src.fetchers.yahoo import fetch_yahoo
from src.fetchers.finnhub import fetch_quote, fetch_news
from src.fetchers.newsapi import fetch_news as fetch_newsapi
from src.preprocess.cleaner import clean_historical, clean_info
from src.preprocess.merge_data import merge_data
from src.technical.indicators import compute_rsi
from src.ai.gemini import explain
from src.telegram.bot import send_message
from src.utils.logger import logger
import pandas as pd

def load_tickers(mode):
    _, tickers_dict = get_categories()
    # watchlist from DB
    if mode == 'watchlist':
        supabase = get_supabase()
        res = supabase.table('watchlist').select('ticker').execute()
        return [r['ticker'] for r in res.data]
    # for top_gainers/losers we'd need live scanning, skip for now
    if mode in ('top_gainers', 'top_losers', 'breaking_news', 'high_volume'):
        logger.info(f"Mode {mode} requires live scanner, using empty list.")
        return []
    return tickers_dict.get(mode, [])

def should_analyze(ticker, timeframe_days=30):
    supabase = get_supabase()
    today = date.today()
    res = supabase.table('posted_analysis')\
        .select('*')\
        .eq('ticker', ticker)\
        .gte('expiry_date', today.isoformat())\
        .execute()
    return len(res.data) == 0  # return True if no recent valid post

def run_analysis(ticker):
    logger.info(f"Analyzing {ticker}")
    # 1. Fetch data
    y_hist, y_info = fetch_yahoo(ticker)
    if y_hist is None or y_hist.empty:
        logger.warning(f"No data from Yahoo for {ticker}")
        return None
    cleaned_hist = clean_historical(y_hist)
    cleaned_info = clean_info(y_info)
    f_quote = fetch_quote(ticker)
    # news
    today = date.today()
    from_str = (today - timedelta(days=2)).isoformat()
    to_str = today.isoformat()
    f_news = fetch_news(ticker, from_str, to_str)
    n_articles = fetch_newsapi(ticker.replace('.NS', ''), from_str, to_str)  # rough query
    merged = merge_data(ticker, cleaned_hist, cleaned_info, f_quote, n_articles, f_news)

    # 2. Technical (simple RSI)
    close_prices = cleaned_hist['Close']
    rsi_series = compute_rsi(close_prices)
    latest_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50

    # 3. Build prompt
    prompt = f"""Analyze {ticker} stock.
Current RSI: {latest_rsi:.2f}
Fundamental info: {cleaned_info}
Recent news headlines: {[a.get('title') for a in n_articles[:5]]}
Give a concise recommendation with target, support, resistance, stoploss, risk, confidence (0-100)."""
    ai_response = explain(prompt)

    # 4. (Optional) generate chart (skip for now)
    # ...

    # 5. Format message
    message = f"📈 *{ticker}*\n━━━━━━━\n{ai_response}\n\n_Confidence: {latest_rsi} (based on RSI only, for demo)_"

    return message

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', required=True)
    args = parser.parse_args()

    mode = args.mode
    logger.info(f"Starting mode: {mode}")
    tickers = load_tickers(mode)
    if not tickers:
        logger.info(f"No tickers for mode {mode}")
        return

    supabase = get_supabase()
    for ticker in tickers:
        if not should_analyze(ticker):
            logger.info(f"Skipping {ticker} (already posted recently)")
            continue
        msg = run_analysis(ticker)
        if msg:
            send_message(msg)
            # insert into posted_analysis
            supabase.table('posted_analysis').insert({
                'ticker': ticker,
                'category': mode,
                'expiry_date': (date.today() + timedelta(days=30)).isoformat(),
                'confidence': 70,  # placeholder
                'report_summary': msg[:200]
            }).execute()
            logger.info(f"Posted {ticker}")

if __name__ == '__main__':
    main()

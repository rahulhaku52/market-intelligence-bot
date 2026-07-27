import argparse, os, time, json, traceback
from datetime import date, timedelta, datetime
import pytz
from src.utils.logger import logger
from src.utils.config_loader import get_categories
from src.database.supabase_client import get_supabase
from src.database.queries import should_analyze
from src.fetchers.yahoo import fetch as yfetch
from src.fetchers.finnhub import fetch_quote, fetch_news
from src.fetchers.newsapi import fetch_news as newsapi_fetch
from src.preprocess.cleaner import clean_historical, clean_info
from src.preprocess.merge_data import merge
from src.technical.score import technical_score
from src.technical.support_resistance import find_levels
from src.technical.indicators import rsi, atr, macd, ema
from src.fundamental.metrics import extract_fundamentals
from src.sentiment.news_score import score_articles
from src.news_enhanced.dedup import remove_duplicates
from src.news_enhanced.source_weight import weight_articles
from src.news_enhanced.event_classifier import classify_event
from src.scanners.volume_scanner import detect_volume_spike, detect_gap, breakout
from src.confidence.engine import compute_confidence
from src.risk.risk_engine import compute_risk
from src.ai.gemini import generate_structured_analysis
from src.chart_renderer.plot import generate_chart
from src.telegram.bot import send_analysis
from src.queue_manager.priority import sort_by_priority
from src.calendar.nse_calendar import is_market_open
from src.backtesting.engine import record_signal, evaluate_closed_signals
import pandas as pd

IST = pytz.timezone('Asia/Kolkata')

def load_tickers(mode):
    _, tickers_dict = get_categories()
    if mode == 'watchlist':
        supabase = get_supabase()
        if supabase:
            try:
                res = supabase.table('watchlist').select('ticker').execute()
                return [r['ticker'] for r in res.data]
            except Exception as e:
                logger.error(f"Watchlist fetch failed: {e}")
                return []
        else:
            logger.warning("Supabase not available for watchlist.")
            return []
    return tickers_dict.get(mode, [])

def get_market_alignment(ticker):
    try:
        nifty_hist, _ = yfetch('^NSEI', period='5d')
        if nifty_hist is None or nifty_hist.empty:
            return 50
        nifty_ret = nifty_hist['Close'].pct_change().iloc[-1]
        stock_hist, _ = yfetch(ticker, period='5d')
        if stock_hist is None or stock_hist.empty:
            return 50
        stock_ret = stock_hist['Close'].pct_change().iloc[-1]
        if (nifty_ret > 0 and stock_ret > 0) or (nifty_ret < 0 and stock_ret < 0):
            return 90
        else:
            return 30
    except:
        return 50

def get_sector_alignment(ticker):
    return 50

def get_earnings_penalty(ticker):
    return 0

def multi_timeframe_agreement(df):
    if df is None or df.empty:
        return 0
    close = df['Close']
    ema20 = ema(close, 20)
    current = close.iloc[-1]
    daily_trend = current > ema20.iloc[-1]
    weekly = close.resample('W').last().dropna()
    if len(weekly) < 2:
        weekly_trend = daily_trend
    else:
        ema20_w = ema(weekly, 5)
        weekly_trend = weekly.iloc[-1] > ema20_w.iloc[-1]
    if daily_trend and weekly_trend:
        return 100
    elif daily_trend or weekly_trend:
        return 50
    else:
        return 0

def run_full_analysis(ticker, mode):
    logger.info(f"🔍 God-Level Analysis: {ticker}")
    try:
        # 1. Yahoo Fetch
        y_hist, y_info = yfetch(ticker)
        if y_hist is None or y_hist.empty:
            logger.warning(f"No Yahoo data for {ticker}, skipping.")
            return None
        y_hist = clean_historical(y_hist)
        if y_hist is None or y_hist.empty:
            logger.warning(f"Yahoo data empty after cleaning for {ticker}")
            return None

        # 2. Clean info
        y_info = clean_info(y_info)

        # 3. Finnhub (safe, returns None/[] on error)
        f_quote = fetch_quote(ticker)
        today = date.today()
        f_news = fetch_news(ticker, (today - timedelta(2)).isoformat(), today.isoformat())

        # 4. NewsAPI (safe, returns [])
        n_articles = newsapi_fetch(ticker.replace('.NS', ''), (today - timedelta(2)).isoformat(), today.isoformat())

        # 5. Merge data (just dictionary)
        data = merge(ticker, y_hist, y_info, f_quote, n_articles, f_news)

        # 6. Technical calculations
        close = y_hist['Close']
        latest_price = close.iloc[-1]

        tech_score = technical_score(y_hist, latest_price)
        mtf = multi_timeframe_agreement(y_hist)
        tech_score = int(tech_score * 0.9 + mtf * 0.1)

        # 7. Fundamental
        fund = extract_fundamentals(y_info)
        fund_score = 50
        pe = fund.get('PE')
        roe = fund.get('ROE')
        if pe and pe > 0:
            if pe < 15: fund_score += 25
            elif pe < 25: fund_score += 10
            elif pe > 50: fund_score -= 15
        if roe and roe > 0.15: fund_score += 20
        fund_score = max(0, min(100, fund_score))

        # 8. News sentiment
        all_articles = n_articles + [{'title': a['headline'], 'description': a['summary'], 'source': {'name': 'Finnhub'}} for a in f_news]
        all_articles = remove_duplicates(all_articles)
        all_articles = weight_articles(all_articles)
        sentiment = score_articles(all_articles)
        sentiment_norm = (sentiment + 30) / 60 * 100

        # 9. Volume & Gap
        vol_spike = detect_volume_spike(y_hist)
        gap = detect_gap(y_hist)
        vol_score = 90 if vol_spike else (70 if gap else 50)

        # 10. Market / sector alignment
        market_align = get_market_alignment(ticker)
        sector_align = get_sector_alignment(ticker)
        earnings_penalty = get_earnings_penalty(ticker)

        # 11. Confidence & Risk
        confidence = compute_confidence(
            tech_score, fund_score, sentiment_norm, vol_score,
            market_align, sector_align, earnings_penalty, mtf
        )

        supports, resistances = find_levels(close)
        support = supports[0] if supports else latest_price * 0.98
        resistance = resistances[0] if resistances else latest_price * 1.02

        atr_val = atr(y_hist).iloc[-1]
        atr_pct = atr_val / latest_price * 100
        volatility = close.pct_change().std()
        news_risk = sum(1 for a in all_articles if classify_event(a) in ['geopolitical', 'rbi_policy']) * 5
        risk = compute_risk(confidence, atr_pct, volatility, gap, news_risk)

        target = resistance * 1.05
        stoploss = support * 0.97

        # 12. AI analysis
        analysis_data = {
            'technical_score': tech_score,
            'fundamental_score': fund_score,
            'news_score': int(sentiment_norm),
            'volume_signal': 'Spike' if vol_spike else ('Gap_' + gap if gap else 'Normal'),
            'confidence': confidence,
            'risk': risk,
            'support': support,
            'resistance': resistance,
            'target': target,
            'stoploss': stoploss
        }
        ai_response = generate_structured_analysis(analysis_data)

        # 13. Chart
        chart = generate_chart(y_hist, ticker, support, resistance)

        # 14. Build message
        message = (
    f"📈 <b>{ticker}</b>\n"
    f"━━━━━━━━━━━\n"
    f"🎯 Target: {ai_response.get('target', target):.2f}\n"
    f"🛑 Stop Loss: {ai_response.get('stop_loss', stoploss):.2f}\n"
    f"📊 Confidence: {ai_response.get('confidence', confidence)}%\n"
    f"⚖ Risk: {ai_response.get('risk', risk)}\n\n"
    f"{ai_response.get('summary', '')}"
)

        # 15. Backtest recording
        record_signal(ticker, mode, latest_price, target, stoploss, confidence)

        return {
            'ticker': ticker,
            'message': message,
            'chart': chart,
            'confidence': confidence,
            'category': mode,
            'priority': 50
        }
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        logger.error(traceback.format_exc())
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', required=True)
    parser.add_argument('--force', action='store_true', help='Force run even if market closed')
    args = parser.parse_args()
    mode = args.mode
    force = args.force

    logger.info(f"Starting God-Level Pipeline v2.0 for {mode} (force={force})")

    if not force and not is_market_open():
        logger.info("Market closed or holiday. Skipping analysis. Use --force to override.")
        return

    try:
        evaluate_closed_signals()
    except Exception as e:
        logger.error(f"Backtest evaluation failed, continuing: {e}")

    tickers = load_tickers(mode)
    if not tickers:
        logger.info(f"No tickers for {mode}")
        return

    signals = []
    for ticker in tickers:
        if not should_analyze(ticker, mode):
            logger.info(f"⏭️ Skipping {ticker} (cooldown)")
            continue
        analysis = run_full_analysis(ticker, mode)
        if analysis:
            if mode == 'breaking_news': analysis['priority'] = 100
            elif mode == 'high_volume': analysis['priority'] = 95
            elif mode == 'watchlist': analysis['priority'] = 90
            elif mode == 'large_cap': analysis['priority'] = 50
            else: analysis['priority'] = 40
            signals.append(analysis)
        time.sleep(0.5)

    signals = sort_by_priority(signals)
    supabase = get_supabase()
    for sig in signals:
        try:
            send_analysis(sig['message'], sig['chart'])
            if supabase:
                try:
                    supabase.table('posted_analysis').insert({
                        'ticker': sig['ticker'],
                        'category': sig['category'],
                        'expiry_date': (date.today() + timedelta(days=30)).isoformat(),
                        'confidence': sig['confidence'],
                        'report_summary': sig['message'][:200]
                    }).execute()
                except Exception as e:
                    logger.error(f"Failed to save analysis: {e}")
            logger.info(f"✅ Posted {sig['ticker']}")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Failed to send {sig['ticker']}: {e}")

if __name__ == '__main__':
    main()

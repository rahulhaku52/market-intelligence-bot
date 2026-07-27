import argparse, os, time, json, traceback
from datetime import date, timedelta
from src.utils.logger import logger
from src.database.supabase_client import get_supabase
from src.database.queries import should_analyze
from src.fetchers.yahoo import fetch as yfetch
from src.fetchers.finnhub import fetch_quote, fetch_news
from src.fetchers.newsapi import fetch_news as newsapi_fetch
from src.preprocess.cleaner import clean_historical, clean_info
from src.preprocess.merge_data import merge
from src.technical.score import technical_score
from src.technical.support_resistance import find_levels
from src.technical.indicators import rsi, macd, ema, atr, bollinger
from src.technical.trendline import trendline_slope
from src.fundamental.metrics import extract_fundamentals
from src.sentiment.news_score import score_articles
from src.news_enhanced.dedup import remove_duplicates
from src.news_enhanced.source_weight import weight_articles
from src.news_enhanced.event_classifier import classify_event
from src.scanners.volume_scanner import detect_volume_spike, detect_gap
from src.confidence.engine import compute_confidence
from src.risk.risk_engine import compute_risk
from src.ai.gemini import generate_structured_analysis
from src.chart_renderer.plot import generate_chart
from src.telegram.bot import send_analysis
from src.queue_manager.priority import sort_by_priority
from src.backtesting.engine import record_signal, evaluate_closed_signals
from src.scanners.auto_scanner import load_symbols, fetch_volume_batch, scan_volume_spikes
import pandas as pd

def load_tickers(mode):
    # Always use dynamic scanner from CSV
    symbols = load_symbols()
    if not symbols:
        return []
    vol_data = fetch_volume_batch(symbols)
    tickers = scan_volume_spikes(vol_data, min_ratio=2.0, top_n=3)
    logger.info(f"Auto tickers: {tickers}")
    return tickers

def run_full_analysis(ticker, mode):
    logger.info(f"🔍 God-Level Analysis: {ticker}")
    try:
        # Daily data (3 months)
        y_hist, y_info = yfetch(ticker, period="3mo", interval="1d")
        if y_hist is None or y_hist.empty:
            logger.warning(f"No daily data for {ticker}")
            return None
        y_hist = clean_historical(y_hist)
        y_info = clean_info(y_info)

        # Weekly data (6 months)
        weekly_hist, _ = yfetch(ticker, period="6mo", interval="1wk")
        if weekly_hist is not None and not weekly_hist.empty:
            weekly_hist = clean_historical(weekly_hist)
        else:
            weekly_hist = None

        # Finnhub & News
        f_quote = fetch_quote(ticker)
        today = date.today()
        f_news = fetch_news(ticker, (today - timedelta(2)).isoformat(), today.isoformat())
        n_articles = newsapi_fetch(ticker.replace('.NS',''), (today - timedelta(2)).isoformat(), today.isoformat())
        data = merge(ticker, y_hist, y_info, f_quote, n_articles, f_news)

        # ---- DAILY INDICATORS ----
        close_daily = y_hist['Close']
        latest_price = close_daily.iloc[-1]
        rsi_daily = rsi(close_daily).iloc[-1]
        macd_line, macd_signal = macd(close_daily)
        macd_daily = macd_line.iloc[-1] - macd_signal.iloc[-1]
        atr_daily = atr(y_hist).iloc[-1]
        bb_upper_d, bb_mid_d, bb_lower_d = bollinger(close_daily)
        bb_upper = bb_upper_d.iloc[-1]
        bb_mid = bb_mid_d.iloc[-1]
        bb_lower = bb_lower_d.iloc[-1]
        supports, resistances = find_levels(close_daily)
        support = supports[0] if supports else latest_price * 0.98
        resistance = resistances[0] if resistances else latest_price * 1.02
        trend_slope = trendline_slope(ema(close_daily, 20), last_n=10)

        # ---- WEEKLY INDICATORS ----
        if weekly_hist is not None:
            close_weekly = weekly_hist['Close']
            weekly_rsi_val = rsi(close_weekly).iloc[-1]
            weekly_macd_line, weekly_macd_signal = macd(close_weekly)
            weekly_macd = weekly_macd_line.iloc[-1] - weekly_macd_signal.iloc[-1]
            weekly_close = close_weekly.iloc[-1]
            weekly_vol = weekly_hist['Volume'].iloc[-1] if len(weekly_hist) > 0 else 0
        else:
            weekly_rsi_val, weekly_macd, weekly_close, weekly_vol = 0, 0, latest_price, 0

        # Fundamental
        fund = extract_fundamentals(y_info)
        pe = fund.get('PE')
        roe = fund.get('ROE')
        de = fund.get('Debt/Equity')
        rev_growth = fund.get('Revenue Growth')

        # News sentiment
        all_articles = n_articles + [{'title': a['headline'], 'description': a['summary'], 'source': {'name': 'Finnhub'}} for a in f_news]
        all_articles = remove_duplicates(all_articles)
        all_articles = weight_articles(all_articles)
        sentiment = score_articles(all_articles)
        sentiment_norm = (sentiment + 30) / 60 * 100

        # Volume & Gap
        vol_spike = detect_volume_spike(y_hist)
        gap = detect_gap(y_hist)

        # Confidence & Risk
        tech_score = technical_score(y_hist, latest_price)
        confidence = compute_confidence(
            tech_score, 50, sentiment_norm, 90 if vol_spike else 50,
            50, 50, 0, 50
        )
        risk = compute_risk(confidence, atr_daily/latest_price*100, close_daily.pct_change().std(), gap, 0)

        # Target & StopLoss (will be overridden by AI, but used as fallback)
        target = resistance * 1.05
        stoploss = support * 0.97

        # AI structured report
        analysis_data = {
            'ticker': ticker,
            'latest_price': f"{latest_price:.2f}",
            'rsi': f"{rsi_daily:.1f}",
            'macd': f"{macd_daily:.4f}",
            'atr': f"{atr_daily:.2f}",
            'bb_upper': f"{bb_upper:.2f}",
            'bb_middle': f"{bb_mid:.2f}",
            'bb_lower': f"{bb_lower:.2f}",
            'support': f"{support:.2f}",
            'resistance': f"{resistance:.2f}",
            'trend_slope': f"{trend_slope:.4f}",
            'weekly_close': f"{weekly_close:.2f}",
            'weekly_rsi': f"{weekly_rsi_val:.1f}",
            'weekly_macd': f"{weekly_macd:.4f}",
            'weekly_volume': f"{weekly_vol:.0f}",
            'pe': pe if pe else 'N/A',
            'roe': roe if roe else 'N/A',
            'de': de if de else 'N/A',
            'rev_growth': rev_growth if rev_growth else 'N/A',
            'news_score': int(sentiment_norm),
            'volume_signal': 'Spike' if vol_spike else 'Normal',
            # Missing keys added for fallback
            'confidence': confidence,
            'risk': risk,
            'target': target,
            'stoploss': stoploss
        }
        ai_response = generate_structured_analysis(analysis_data)

        # Build chart
        chart = generate_chart(y_hist, ticker, support, resistance)

        # Build Telegram message (HTML)
        message = (
            f"📈 <b>{ticker}</b>\n"
            f"━━━━━━━━━━━\n"
            f"🎯 Short-term Target: {ai_response.get('target_short_term', target)}\n"
            f"🛑 Short-term SL: {ai_response.get('stop_loss_short_term', stoploss)}\n"
            f"📈 Long-term Target: {ai_response.get('target_long_term', target)}\n"
            f"🛑 Long-term SL: {ai_response.get('stop_loss_long_term', stoploss)}\n"
            f"📊 Confidence: {ai_response.get('confidence', confidence)}%\n"
            f"⚖ Risk: {ai_response.get('risk', risk)}\n"
            f"🔹 Entry Zone: {ai_response.get('entry_zone', 'N/A')}\n"
            f"🚩 Exit Signal: {ai_response.get('exit_signal', 'N/A')}\n"
            f"📝 {ai_response.get('summary', '')}"
        )

        record_signal(ticker, mode, latest_price, float(ai_response.get('target_short_term', 0)),
                      float(ai_response.get('stop_loss_short_term', 0)), confidence)

        return {
            'ticker': ticker,
            'message': message,
            'chart': chart,
            'confidence': confidence,
            'category': mode,
            'priority': 100  # top priority
        }
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        logger.error(traceback.format_exc())
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', required=True)
    parser.add_argument('--force', action='store_true', default=True)
    args = parser.parse_args()
    mode = args.mode

    logger.info(f"Starting Dynamic God-Level Scanner (mode={mode})")

    # Backtest evaluation
    try:
        evaluate_closed_signals()
    except Exception as e:
        logger.error(f"Backtest evaluation failed, continuing: {e}")

    tickers = load_tickers(mode)
    if not tickers:
        logger.info("No high volume tickers found.")
        return

    signals = []
    for ticker in tickers:
        if not should_analyze(ticker, mode):
            logger.info(f"⏭️ Skipping {ticker} (cooldown)")
            continue
        analysis = run_full_analysis(ticker, mode)
        if analysis:
            signals.append(analysis)
        time.sleep(1)  # avoid rate limits

    signals = sort_by_priority(signals)
    supabase = get_supabase()
    for sig in signals:
        try:
            send_analysis(sig['message'], sig['chart'])
            if supabase:
                try:
                    supabase.table('posted_analysis').insert({
                        'ticker': sig['ticker'],
                        'category': 'dynamic',
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

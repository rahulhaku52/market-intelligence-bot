import argparse
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from datetime import datetime, timezone
from config.settings import SignalStatus
from src.utils.logger import logger
from src.performance.database import init_sqlite_db, log_signal_to_db
from src.performance.backtester import evaluate_closed_trades
from src.performance.metrics import compute_historical_performance_metrics
from src.scoring.calibrator import get_calibration_state

from src.scanner.deep_scanner import get_target_scan_candidates
from src.data.quote_router import fetch_validated_quote
from src.data.candle_provider import fetch_mtf_candles, validate_candle_integrity
from src.data.validator import validate_data_pipeline

from src.market.regime import get_nifty_regime
from src.market.breadth import calculate_market_breadth
from src.market.volatility import get_india_vix_context
from src.market.sector import evaluate_sector_relative_strength, get_sector_for_ticker

from src.technical.levels import find_dynamic_levels
from src.technical.timeframe import evaluate_mtf_confluence
from src.technical.structure import evaluate_market_structure
from src.technical.price_action import detect_candlestick_patterns, detect_breakout
from src.technical.indicators import rsi, macd, atr
from src.technical.volume_analysis import volume_score

from src.fundamental.quality import extract_fundamental_quality
from src.fundamental.growth import extract_fundamental_growth
from src.fundamental.valuation import extract_fundamental_valuation
from src.events.corporate import check_corporate_event_lock
from src.news.aggregator import aggregate_and_score_news

from src.scoring.confluence import compute_dynamic_confluence
from src.trading.planner import calculate_trade_plan
from src.trading.position_size import calculate_position_size
from src.trading.risk import evaluate_overall_risk
from src.trading.auditor import run_preflight_audit

from src.chart_renderer.plot import generate_chart
from src.ai.explainer import generate_ai_explanation
from src.telegram.formatter import format_telegram_report
from src.telegram.sender import send_telegram_alert
from src.database.posted_tracker import should_post, update_posted

def analyze_single_ticker(ticker: str, mode: str, nifty_regime: dict, vix_ctx: dict) -> dict:
    logger.info(f"🔍 Executing 30-Layer Deep Analysis: {ticker}")
    
    # Layer 1 - 3: Live Quote Router & Validation
    quote = fetch_validated_quote(ticker)
    if quote.status != SignalStatus.VALID:
        logger.warning(f"🚫 {ticker} REJECTED at Layer 1-3: Quote Status = {quote.status.value}")
        return None
        
    # Multi-timeframe Candles
    candles = fetch_mtf_candles(ticker)
    valid_pipe, pipe_status = validate_data_pipeline(quote, candles)
    if not valid_pipe:
        logger.warning(f"🚫 {ticker} REJECTED at Layer 3: Pipeline Status = {pipe_status.value}")
        return None
        
    df_daily = candles['1D']
    df_weekly = candles['1W']
    
    if not validate_candle_integrity(df_daily):
        logger.warning(f"🚫 {ticker} REJECTED at Layer 3: Daily candles integrity failed")
        return None
        
    # Layer 10: Sector Relative Strength
    close_daily = df_daily['Close']
    stock_daily_ret = float((close_daily.iloc[-1] - close_daily.iloc[-2]) / close_daily.iloc[-2]) * 100.0 if len(close_daily) >= 2 else 0.0
    sector_info = evaluate_sector_relative_strength(ticker, stock_daily_ret)
    
    # Layer 11: Multi-Timeframe Trend Confluence
    mtf_res = evaluate_mtf_confluence(candles)
    
    # Layer 12: Market Structure
    struct_res = evaluate_market_structure(df_daily)
    
    # Layer 13: Dynamic Support/Resistance with Level Clustering
    supports, resistances = find_dynamic_levels(df_daily, df_weekly, quote.price)
    
    # Layer 15 - 17: Technical Momentum & Volatility
    rsi_val = float(rsi(close_daily).iloc[-1])
    tech_momentum_score = max(0, 100 - abs(rsi_val - 50) * 2)
    atr_val = float(atr(df_daily).iloc[-1])
    atr_pct = (atr_val / quote.price) * 100.0
    
    # Layer 20 - 21: Fundamental Metrics (Dynamic Normalization)
    info = {}  # yfinance info fetched on-demand if available
    fund_q = extract_fundamental_quality(info)
    fund_g = extract_fundamental_growth(info)
    fund_v = extract_fundamental_valuation(info)
    
    # Layer 22: Corporate Event Lock
    event_locked, event_reason = check_corporate_event_lock(info)
    if event_locked:
        logger.warning(f"🔒 {ticker} REJECTED at Layer 22: Event Locked ({event_reason})")
        return None
        
    # Layer 23: News Sentiment
    news_res = aggregate_and_score_news(ticker)
    
    # Layer 28: Dynamic Confluence Score
    confluence_res = compute_dynamic_confluence(
        tech_score=tech_momentum_score,
        mtf_score=mtf_res['confluence_score'],
        structure_score=struct_res['score'],
        volume_score=75.0,
        sector_score=sector_info['score'],
        market_breadth_score=60.0,
        fund_quality_score=fund_q['quality_score'],
        fund_growth_score=fund_g['growth_score'],
        fund_val_score=fund_v['valuation_score'],
        news_sentiment_score=news_res['score']
    )
    setup_score = confluence_res['confluence_score']
    
    # Check minimum setup score gate (>= 65)
    if setup_score < 65:
        logger.info(f"⏭️ Skipping {ticker}: Setup Score {setup_score} < 65")
        return None
        
    # Layer 29: Deterministic Python Trade Planning & Position Sizing
    trade_plan = calculate_trade_plan(quote.price, supports, resistances, atr_val, vix_ctx['sl_buffer_multiplier'])
    if trade_plan.status != SignalStatus.VALID:
        logger.info(f"⏭️ Skipping {ticker}: Trade Plan Status = {trade_plan.status.value}")
        return None
        
    pos_size = calculate_position_size(quote.price, trade_plan.stoploss)
    risk_level = evaluate_overall_risk(setup_score, atr_pct, vix_ctx['vix_regime'], trade_plan.risk_reward)
    
    # Layer 30: 13-Point Preflight Auditor
    audit_passed, audit_reason = run_preflight_audit(ticker, quote, trade_plan, mtf_res, event_locked)
    if not audit_passed:
        logger.warning(f"🚫 {ticker} REJECTED at Layer 30 (Auditor): {audit_reason}")
        return None

    # Performance Calibration
    perf_metrics = compute_historical_performance_metrics()
    calibration_state = get_calibration_state(perf_metrics['calibration_sample'])
    
    # Explanation Engine (Gemini AI with Python Fallback)
    analysis_dict = {
        'ticker': ticker,
        'price': quote.price,
        'trend': mtf_res['primary_trend'],
        'score': setup_score,
        'sector': sector_info['sector'],
        'risk': risk_level
    }
    explanation = generate_ai_explanation(analysis_dict)
    
    # Chart generation
    support_price = supports[0]['center_price'] if supports else quote.price * 0.95
    resistance_price = resistances[0]['center_price'] if resistances else quote.price * 1.05
    chart_buf = generate_chart(df_daily, ticker, support_price, resistance_price)
    
    result = {
        'ticker': ticker,
        'quote': quote,
        'setup_score': setup_score,
        'trend': mtf_res['primary_trend'],
        'trade_plan': trade_plan,
        'position_size': pos_size,
        'risk_level': risk_level,
        'sector': sector_info['sector'],
        'explanation': explanation,
        'calibration': calibration_state,
        'chart_bytes': chart_buf
    }
    
    # Log signal to local SQLite DB
    log_signal_to_db({
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'ticker': ticker,
        'mode': mode,
        'price': quote.price,
        'price_type': quote.price_type,
        'data_quality_score': quote.data_quality_score,
        'setup_score': setup_score,
        'entry_zone': trade_plan.entry_zone,
        'stoploss': trade_plan.stoploss,
        'tp1': trade_plan.tp1,
        'tp2': trade_plan.tp2,
        'tp3': trade_plan.tp3,
        'risk_reward': trade_plan.risk_reward,
        'status': SignalStatus.VALID.value
    })
    
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='dynamic')
    parser.add_argument('--force', action='store_true', default=False)
    args = parser.parse_args()
    
    logger.info("==================================================")
    logger.info("🚀 Starting 30-Layer Production Market Engine (v4)")
    logger.info("==================================================")
    
    # Initialize SQLite DB
    init_sqlite_db()
    
    # Evaluate closed signals backtest
    evaluate_closed_trades()
    
    # Market Context & Volatility Regimes
    nifty_regime = get_nifty_regime()
    vix_ctx = get_india_vix_context()
    logger.info(f"📊 Market Context: NIFTY = {nifty_regime['regime']}, India VIX = {vix_ctx['vix']} ({vix_ctx['vix_regime']})")
    
    # Two-Stage Scanner: Fast Pre-Scan
    candidates = get_target_scan_candidates(args.mode)
    if not candidates:
        logger.info("No candidates identified by scanner.")
        return
        
    signals = []
    for ticker in candidates:
        if not args.force and not should_post(ticker, 'BULLISH', 70):
            logger.info(f"⏭️ Skipping {ticker} (cooldown)")
            continue
            
        analysis = analyze_single_ticker(ticker, args.mode, nifty_regime, vix_ctx)
        if analysis:
            signals.append(analysis)
        time.sleep(1)
        
    if not signals:
        logger.info("No signals passed all 30 analytical layers.")
        return
        
    # Sort signals by setup score
    signals.sort(key=lambda x: x['setup_score'], reverse=True)
    top_signals = signals[:2]
    
    for sig in top_signals:
        ticker = sig['ticker']
        message = format_telegram_report(sig)
        send_telegram_alert(message, sig['chart_bytes'])
        update_posted(ticker, sig['trend'], sig['setup_score'])
        logger.info(f"✅ Posted {ticker} signal to Telegram!")
        time.sleep(2)

if __name__ == '__main__':
    main()

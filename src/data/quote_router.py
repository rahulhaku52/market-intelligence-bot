import time
from datetime import datetime, timezone
import yfinance as yf
from config.settings import (
    SessionState, SignalStatus,
    MAX_ALLOWED_PRICE_DEVIATION_BPS, STALE_QUOTE_THRESHOLD_SECONDS
)
from src.market.nse_calendar import get_current_session_state
from src.utils.logger import logger

class ValidatedQuote:
    def __init__(self, ticker, price, price_type, age_seconds, sources_count, deviation_bps, data_quality_score, status):
        self.ticker = ticker
        self.price = price
        self.price_type = price_type          # 'LIVE' or 'CLOSE'
        self.age_seconds = age_seconds
        self.sources_count = sources_count
        self.deviation_bps = deviation_bps
        self.data_quality_score = data_quality_score
        self.status = status                  # SignalStatus enum

def fetch_validated_quote(ticker: str) -> ValidatedQuote:
    session_state = get_current_session_state()
    ticker_obj = yf.Ticker(ticker)
    
    # Provider A: Fast Info
    p_a = None
    t_a = time.time()
    try:
        fast = ticker_obj.fast_info
        p_a = fast.get('lastPrice') or fast.get('regularMarketPrice') or fast.get('previousClose')
    except Exception as e:
        logger.warning(f"Fast info fetch error for {ticker}: {e}")

    # Provider B: 1-minute intraday candle
    p_b = None
    t_b = time.time()
    try:
        intraday = ticker_obj.history(period='1d', interval='1m')
        if intraday is not None and not intraday.empty:
            p_b = float(intraday['Close'].iloc[-1])
            # get candle timestamp
            last_dt = intraday.index[-1]
            if hasattr(last_dt, 'timestamp'):
                t_b = last_dt.timestamp()
    except Exception as e:
        logger.warning(f"Intraday history fetch error for {ticker}: {e}")

    # Evaluate availability
    if p_a is None and p_b is None:
        return ValidatedQuote(ticker, 0.0, "UNKNOWN", 999999, 0, 0.0, 0, SignalStatus.DATA_REJECTED)

    sources = [p for p in (p_a, p_b) if p is not None and p > 0]
    sources_count = len(sources)
    final_price = sources[0]
    
    # Calculate Bps deviation if 2 independent feeds present
    deviation_bps = 0.0
    if sources_count >= 2:
        diff = abs(sources[0] - sources[1])
        avg = (sources[0] + sources[1]) / 2.0
        deviation_bps = (diff / avg) * 10000.0
        final_price = avg

    # Age calculation
    quote_age = max(0, int(time.time() - min(t_a, t_b)))
    
    # Determine price type and freshness rule according to market session state
    if session_state == SessionState.REGULAR:
        price_type = "LIVE"
        if quote_age > STALE_QUOTE_THRESHOLD_SECONDS:
            logger.warning(f"Stale quote for {ticker}: age {quote_age}s > {STALE_QUOTE_THRESHOLD_SECONDS}s")
            return ValidatedQuote(ticker, final_price, price_type, quote_age, sources_count, deviation_bps, 30, SignalStatus.STALE_PRICE)
    else:
        price_type = "CLOSE"
        quote_age = 0  # In non-market hours, latest close is expected

    # Bps Deviation threshold guard
    if sources_count >= 2 and deviation_bps > MAX_ALLOWED_PRICE_DEVIATION_BPS:
        logger.warning(f"Price deviation mismatch for {ticker}: {deviation_bps:.2f} bps > {MAX_ALLOWED_PRICE_DEVIATION_BPS} bps")
        return ValidatedQuote(ticker, final_price, price_type, quote_age, sources_count, deviation_bps, 40, SignalStatus.SOURCE_MISMATCH)

    # Compute Data Quality Score (0-100)
    data_quality_score = 100
    if sources_count < 2:
        data_quality_score -= 10
    if deviation_bps > 10:
        data_quality_score -= min(30, int(deviation_bps))
    if quote_age > 60 and session_state == SessionState.REGULAR:
        data_quality_score -= min(30, int(quote_age / 10))

    if data_quality_score < 70:
        status = SignalStatus.DATA_REJECTED
    else:
        status = SignalStatus.VALID

    return ValidatedQuote(
        ticker=ticker,
        price=float(final_price),
        price_type=price_type,
        age_seconds=quote_age,
        sources_count=sources_count,
        deviation_bps=round(deviation_bps, 2),
        data_quality_score=data_quality_score,
        status=status
    )

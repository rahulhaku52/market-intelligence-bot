import yfinance as yf
from src.utils.logger import logger

def get_nifty_regime():
    """
    Analyzes NIFTY 50 index (^NSEI) to return market regime:
    Returns dict: {'regime': 'BULLISH'/'BEARISH'/'SIDEWAYS', 'nifty_close': float, 'ema20': float, 'ema50': float}
    """
    try:
        nifty = yf.Ticker("^NSEI").history(period="6mo", interval="1d")
        if nifty is None or nifty.empty or len(nifty) < 50:
            return {'regime': 'SIDEWAYS', 'nifty_close': 0.0, 'ema20': 0.0, 'ema50': 0.0}
            
        close = nifty['Close']
        ema20 = close.ewm(span=20).mean().iloc[-1]
        ema50 = close.ewm(span=50).mean().iloc[-1]
        latest = close.iloc[-1]
        
        if latest > ema20 and ema20 > ema50:
            regime = 'BULLISH'
        elif latest < ema20 and ema20 < ema50:
            regime = 'BEARISH'
        else:
            regime = 'SIDEWAYS'
            
        return {
            'regime': regime,
            'nifty_close': round(float(latest), 2),
            'ema20': round(float(ema20), 2),
            'ema50': round(float(ema50), 2)
        }
    except Exception as e:
        logger.warning(f"Failed to fetch NIFTY regime: {e}")
        return {'regime': 'SIDEWAYS', 'nifty_close': 0.0, 'ema20': 0.0, 'ema50': 0.0}

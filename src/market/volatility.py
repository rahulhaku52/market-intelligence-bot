import yfinance as yf
from src.utils.logger import logger

def get_india_vix_context():
    """
    Fetches India VIX (^INDIAVIX) context:
    Returns dict: {'vix': float, 'vix_regime': 'LOW'/'NORMAL'/'HIGH', 'sl_buffer_multiplier': float}
    """
    try:
        vix_df = yf.Ticker("^INDIAVIX").history(period="1mo", interval="1d")
        if vix_df is None or vix_df.empty:
            return {'vix': 15.0, 'vix_regime': 'NORMAL', 'sl_buffer_multiplier': 1.0}
            
        vix_val = float(vix_df['Close'].iloc[-1])
        
        if vix_val < 12.0:
            regime = 'LOW'
            multiplier = 0.8
        elif vix_val > 20.0:
            regime = 'HIGH'
            multiplier = 1.4
        else:
            regime = 'NORMAL'
            multiplier = 1.0
            
        return {
            'vix': round(vix_val, 2),
            'vix_regime': regime,
            'sl_buffer_multiplier': multiplier
        }
    except Exception as e:
        logger.warning(f"Failed to fetch India VIX: {e}")
        return {'vix': 15.0, 'vix_regime': 'NORMAL', 'sl_buffer_multiplier': 1.0}

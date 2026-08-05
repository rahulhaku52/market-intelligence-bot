import yfinance as yf
import pandas as pd
from src.utils.logger import logger

def fetch_mtf_candles(ticker: str):
    """
    Fetches multi-timeframe candle datasets for a given ticker:
    - Weekly (1W, 1 year history)
    - Daily (1D, 6 months history)
    - 60m / 1H (60m, 1 month history)
    - 30m (30m, 1 month history)
    - 15m (15m, 1 month history)
    """
    stock = yf.Ticker(ticker)
    candles = {}
    
    timeframe_map = {
        '1W': ('1y', '1wk'),
        '1D': ('6mo', '1d'),
        '60m': ('1mo', '60m'),
        '30m': ('1mo', '30m'),
        '15m': ('1mo', '15m')
    }
    
    for tf, (period, interval) in timeframe_map.items():
        try:
            df = stock.history(period=period, interval=interval)
            if df is not None and not df.empty and len(df) >= 5:
                df = df.dropna()
                candles[tf] = df
            else:
                candles[tf] = None
        except Exception as e:
            logger.warning(f"Failed to fetch {tf} candles for {ticker}: {e}")
            candles[tf] = None

    return candles

def validate_candle_integrity(df: pd.DataFrame) -> bool:
    if df is None or df.empty or len(df) < 5:
        return False
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in df.columns for col in required_cols):
        return False
    # Check for negative prices or zeros
    if (df['Close'] <= 0).any() or (df['High'] < df['Low']).any():
        return False
    return True

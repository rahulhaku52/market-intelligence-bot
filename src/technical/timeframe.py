import pandas as pd
from src.technical.indicators import rsi, macd, ema, vwap

def evaluate_single_timeframe(df: pd.DataFrame, tf_name: str) -> dict:
    if df is None or df.empty or len(df) < 20:
        return {
            'timeframe': tf_name,
            'trend': 'NEUTRAL',
            'momentum': 50.0,
            'last_swing_high': 0.0,
            'last_swing_low': 0.0,
            'distance_from_vwap_pct': 0.0
        }
        
    close = df['Close']
    latest_close = close.iloc[-1]
    
    # EMA 20 vs 50 trend
    ema20 = ema(close, 20).iloc[-1]
    ema50 = ema(close, 50).iloc[-1] if len(df) >= 50 else ema20
    
    if latest_close > ema20 and ema20 >= ema50:
        trend = 'BULLISH'
    elif latest_close < ema20 and ema20 <= ema50:
        trend = 'BEARISH'
    else:
        trend = 'NEUTRAL'
        
    # Momentum (RSI)
    rsi_val = float(rsi(close).iloc[-1])
    
    # Swings
    highs = df['High']
    lows = df['Low']
    last_swing_high = float(highs.rolling(10).max().iloc[-1])
    last_swing_low = float(lows.rolling(10).min().iloc[-1])
    
    # VWAP distance
    vwap_series = vwap(df)
    vwap_val = float(vwap_series.iloc[-1])
    vwap_dist = round(((latest_close - vwap_val) / vwap_val) * 100.0, 2)
    
    return {
        'timeframe': tf_name,
        'trend': trend,
        'momentum': round(rsi_val, 1),
        'last_swing_high': round(last_swing_high, 2),
        'last_swing_low': round(last_swing_low, 2),
        'distance_from_vwap_pct': vwap_dist
    }

def evaluate_mtf_confluence(candles_dict: dict) -> dict:
    """
    Evaluates multi-timeframe confluence across 1W, 1D, 60m, 30m, 15m
    """
    tf_results = {}
    bullish_count = 0
    total_valid = 0
    
    for tf_name, df in candles_dict.items():
        res = evaluate_single_timeframe(df, tf_name)
        tf_results[tf_name] = res
        if res['trend'] == 'BULLISH':
            bullish_count += 1
        if res['trend'] != 'NEUTRAL':
            total_valid += 1
            
    confluence_score = int((bullish_count / max(1, len(candles_dict))) * 100.0)
    
    return {
        'details': tf_results,
        'confluence_score': confluence_score,
        'primary_trend': tf_results.get('1D', {}).get('trend', 'NEUTRAL')
    }

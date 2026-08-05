import pandas as pd

def detect_candlestick_patterns(df: pd.DataFrame) -> dict:
    if df is None or df.empty or len(df) < 3:
        return {'patterns': [], 'score': 50}
        
    c0 = df['Close'].iloc[-1]
    o0 = df['Open'].iloc[-1]
    h0 = df['High'].iloc[-1]
    l0 = df['Low'].iloc[-1]
    
    c1 = df['Close'].iloc[-2]
    o1 = df['Open'].iloc[-2]
    
    patterns = []
    score = 50
    
    # Bullish Engulfing
    if c1 < o1 and c0 > o0 and c0 >= o1 and o0 <= c1:
        patterns.append('BULLISH_ENGULFING')
        score += 20
        
    # Hammer
    body = abs(c0 - o0)
    lower_wick = min(c0, o0) - l0
    if body > 0 and lower_wick >= 2 * body and (h0 - max(c0, o0)) <= body:
        patterns.append('HAMMER')
        score += 15
        
    # Bearish Engulfing
    if c1 > o1 and c0 < o0 and c0 <= o1 and o0 >= c1:
        patterns.append('BEARISH_ENGULFING')
        score -= 20
        
    return {
        'patterns': patterns,
        'score': max(0, min(100, score))
    }

def detect_breakout(df: pd.DataFrame, nearest_resistance: float) -> dict:
    if df is None or df.empty or nearest_resistance <= 0:
        return {'breakout': False, 'score': 50}
        
    close = df['Close'].iloc[-1]
    if close > nearest_resistance * 1.005:  # 0.5% breakout margin
        return {'breakout': True, 'score': 85}
        
    return {'breakout': False, 'score': 50}

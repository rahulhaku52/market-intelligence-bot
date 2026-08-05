import pandas as pd

def evaluate_market_structure(df: pd.DataFrame) -> dict:
    if df is None or df.empty or len(df) < 20:
        return {'structure': 'NEUTRAL', 'score': 50}
        
    highs = df['High']
    lows = df['Low']
    
    recent_high = highs.iloc[-10:].max()
    prev_high = highs.iloc[-20:-10].max()
    
    recent_low = lows.iloc[-10:].min()
    prev_low = lows.iloc[-20:-10].min()
    
    if recent_high > prev_high and recent_low > prev_low:
        structure = 'BULLISH_HH_HL'
        score = 85
    elif recent_high < prev_high and recent_low < prev_low:
        structure = 'BEARISH_LH_LL'
        score = 25
    else:
        structure = 'CONSOLIDATION'
        score = 50
        
    return {'structure': structure, 'score': score}

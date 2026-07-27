def detect_volume_spike(df, factor=2.0):
    if df is None or df.empty: return False
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    last_vol = df['Volume'].iloc[-1]
    return last_vol > avg_vol * factor

def detect_gap(df):
    if df is None or df.empty: return None
    last_close = df['Close'].iloc[-2]
    today_open = df['Open'].iloc[-1]
    if today_open > last_close * 1.02:
        return 'gap_up'
    elif today_open < last_close * 0.98:
        return 'gap_down'
    return None

def breakout(df, resistance):
    if not df.empty and df['Close'].iloc[-1] > resistance * 1.01:
        return True
    return False
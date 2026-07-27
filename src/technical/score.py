from .indicators import rsi, macd, atr, bollinger, ema, vwap
from .support_resistance import find_levels
from .trendline import trendline_slope
from .volume_analysis import volume_score
import pandas as pd

def technical_score(df, latest_price):
    close = df['Close']
    if close.empty: return 50
    # RSI
    rsi_val = rsi(close).iloc[-1]
    rsi_score = max(0, 100 - abs(rsi_val - 50))  # closer to 50 higher

    # MACD
    macd_line, signal_line = macd(close)
    macd_diff = macd_line.iloc[-1] - signal_line.iloc[-1]
    macd_score = 70 if macd_diff > 0 else 30

    # ATR volatility
    atr_val = atr(df).iloc[-1]
    atr_pct = atr_val / latest_price * 100
    # high volatility could be risky, moderate score
    atr_score = 80 if 1 < atr_pct < 3 else 60

    # Bollinger position
    upper, mid, lower = bollinger(close)
    bb_pos = (latest_price - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) if upper.iloc[-1] != lower.iloc[-1] else 0.5
    bb_score = 80 if 0.3 < bb_pos < 0.7 else 50  # middle band healthy

    # Trend strength (slope of EMA20)
    ema20 = ema(close, 20)
    slope = trendline_slope(ema20, last_n=10)
    trend_score = 80 if slope > 0.01 else (70 if slope > -0.01 else 40)

    # Volume score
    vol_score = volume_score(df)

    # Support/Resistance proximity
    supports, resistances = find_levels(close)
    if supports:
        nearest_support = min(supports, key=lambda x: abs(x - latest_price))
    else:
        nearest_support = latest_price * 0.95
    if resistances:
        nearest_resistance = min(resistances, key=lambda x: abs(x - latest_price))
    else:
        nearest_resistance = latest_price * 1.05
    sup_res_score = 80 if (latest_price - nearest_support) < (nearest_resistance - latest_price) else 60

    # Weighted combination
    final = (rsi_score * 0.15 + macd_score * 0.15 + atr_score * 0.1 +
             bb_score * 0.1 + trend_score * 0.15 + vol_score * 0.2 + sup_res_score * 0.15)
    return min(100, int(final))
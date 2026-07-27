import pandas as pd
import numpy as np

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    return macd_line, signal_line

def ema(series, period):
    return series.ewm(span=period).mean()

def sma(series, period):
    return series.rolling(period).mean()

def atr(df, period=14):
    high, low, close = df['High'], df['Low'], df['Close']
    tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def bollinger(series, period=20, std=2):
    sma = series.rolling(period).mean()
    std_dev = series.rolling(period).std()
    upper = sma + std * std_dev
    lower = sma - std * std_dev
    return upper, sma, lower

def fibonacci(high, low):
    diff = high - low
    levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
    return {lvl: low + lvl * diff for lvl in levels}

def vwap(df):
    df = df.copy()
    df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3
    return (df['typical_price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
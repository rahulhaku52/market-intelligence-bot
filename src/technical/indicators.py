import pandas as pd
import numpy as np

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    res = 100 - (100 / (1 + rs))
    return res.fillna(50)

def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    return macd_line, signal_line

def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period).mean()

def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(period).mean()

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df['High'], df['Low'], df['Close']
    tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
    return tr.rolling(period).mean().fillna(high - low)

def bollinger(series: pd.Series, period: int = 20, std: float = 2.0):
    mid = series.rolling(period).mean()
    std_dev = series.rolling(period).std()
    upper = mid + std * std_dev
    lower = mid - std * std_dev
    return upper, mid, lower

def vwap(df: pd.DataFrame) -> pd.Series:
    df_copy = df.copy()
    tp = (df_copy['High'] + df_copy['Low'] + df_copy['Close']) / 3.0
    vol = df_copy['Volume'].replace(0, 1)
    return (tp * vol).cumsum() / vol.cumsum()
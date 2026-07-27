import csv
import os
import yfinance as yf
from src.utils.logger import logger

def load_symbols(csv_path='data/nifty500.csv'):
    symbols = []
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return symbols
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                symbols.append(row[0].strip())
    return symbols

def fetch_volume_batch(symbols, period="1mo"):
    try:
        data = yf.download(tickers=symbols, period=period, group_by='ticker', threads=True, progress=False)
        return data
    except Exception as e:
        logger.error(f"Batch fetch failed: {e}")
        return None

def scan_volume_spikes(batch_data, min_ratio=2.0, top_n=3):
    spikes = []
    if batch_data is None:
        return spikes
    for ticker in batch_data.columns.levels[0]:
        try:
            df = batch_data[ticker].dropna()
            if len(df) < 20:
                continue
            avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
            last_vol = df['Volume'].iloc[-1]
            if avg_vol == 0:
                continue
            ratio = last_vol / avg_vol
            if ratio >= min_ratio:
                spikes.append((ticker, ratio))
        except Exception:
            continue
    spikes.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in spikes[:top_n]]

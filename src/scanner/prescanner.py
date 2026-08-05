import csv
import os
import yfinance as yf
import pandas as pd
from src.utils.logger import logger

def load_universe(csv_path='data/nifty500.csv') -> list[str]:
    symbols = []
    if not os.path.exists(csv_path):
        logger.error(f"Universe CSV not found: {csv_path}")
        return symbols
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                symbols.append(row[0].strip())
    return symbols

def run_fast_prescan(symbols: list[str], top_n: int = 30) -> list[str]:
    """
    Two-Stage Fast Pre-Scanner with Liquidity Filters:
    - Min Price >= INR 20
    - Min 20-day Avg Volume >= 50,000 shares
    - Min Daily Traded Value >= INR 1 Crore
    - RVOL >= 1.2 or Gap/Price Momentum
    """
    if not symbols:
        return []
        
    try:
        logger.info(f"⚡ Fast Pre-Scanning {len(symbols)} universe tickers...")
        data = yf.download(tickers=symbols, period="1mo", group_by='ticker', threads=True, progress=False)
        if data is None or data.empty:
            return symbols[:top_n]
            
        candidates = []
        for ticker in data.columns.levels[0]:
            try:
                df = data[ticker].dropna()
                if len(df) < 20:
                    continue
                    
                close = df['Close']
                volume = df['Volume']
                ltp = float(close.iloc[-1])
                avg_vol = float(volume.rolling(20).mean().iloc[-1])
                last_vol = float(volume.iloc[-1])
                
                # --- LIQUIDITY FILTERS ---
                if ltp < 20.0:  # Ignore penny stocks
                    continue
                if avg_vol < 50000:  # Low volume illiquid stock
                    continue
                turnover = ltp * avg_vol
                if turnover < 10000000.0:  # < 1 Crore INR turnover
                    continue
                    
                # --- PRE-SCAN FACTORS ---
                rvol = last_vol / avg_vol if avg_vol > 0 else 1.0
                price_change_pct = abs((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100.0
                
                # Score candidate
                pre_score = (rvol * 30.0) + (price_change_pct * 10.0)
                if rvol >= 1.2 or price_change_pct >= 2.0:
                    candidates.append((ticker, pre_score))
            except Exception:
                continue
                
        candidates.sort(key=lambda x: x[1], reverse=True)
        selected = [c[0] for c in candidates[:top_n]]
        logger.info(f"✅ Fast Pre-Scanner selected top {len(selected)} candidates: {selected[:10]}...")
        return selected
    except Exception as e:
        logger.error(f"Pre-scanner batch download failed: {e}")
        return symbols[:top_n]

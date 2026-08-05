import yaml
import yfinance as yf
from src.utils.logger import logger

def load_sector_config(path='config/sectors.yaml'):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f).get('sectors', {})
    except Exception:
        return {}

SECTOR_MAP = load_sector_config()

def get_sector_for_ticker(ticker: str) -> str:
    for sector_name, info in SECTOR_MAP.items():
        if ticker in info.get('tickers', []):
            return sector_name
    return 'GENERAL'

def evaluate_sector_relative_strength(ticker: str, stock_daily_return: float) -> dict:
    """
    Evaluates stock relative strength vs its sector index.
    """
    sector_name = get_sector_for_ticker(ticker)
    if sector_name == 'GENERAL' or sector_name not in SECTOR_MAP:
        return {'sector': 'GENERAL', 'sector_return': 0.0, 'outperforming': True, 'score': 50}
        
    index_symbol = SECTOR_MAP[sector_name].get('index')
    try:
        idx_df = yf.Ticker(index_symbol).history(period="5d", interval="1d")
        if idx_df is not None and len(idx_df) >= 2:
            idx_ret = float((idx_df['Close'].iloc[-1] - idx_df['Close'].iloc[-2]) / idx_df['Close'].iloc[-2]) * 100.0
            diff = stock_daily_return - idx_ret
            outperforming = diff > 0
            score = min(100, max(0, int(50 + diff * 10)))
            return {
                'sector': sector_name,
                'sector_return': round(idx_ret, 2),
                'outperforming': outperforming,
                'score': score
            }
    except Exception as e:
        logger.warning(f"Sector relative strength error for {ticker}: {e}")

    return {'sector': sector_name, 'sector_return': 0.0, 'outperforming': True, 'score': 50}

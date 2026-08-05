from src.utils.logger import logger

def calculate_market_breadth(batch_data):
    """
    Calculates Nifty 500 Market Breadth metrics from pre-downloaded batch data:
    - Advances vs Declines ratio
    - Percentage of stocks above 20 EMA and 50 EMA
    """
    if batch_data is None:
        return {'advances_ratio': 1.0, 'pct_above_ema20': 50.0, 'pct_above_ema50': 50.0, 'status': 'NEUTRAL'}
        
    try:
        advances = 0
        declines = 0
        above_ema20 = 0
        above_ema50 = 0
        total = 0
        
        for ticker in batch_data.columns.levels[0]:
            try:
                df = batch_data[ticker].dropna()
                if len(df) < 50:
                    continue
                close = df['Close']
                change = close.iloc[-1] - close.iloc[-2]
                if change > 0:
                    advances += 1
                elif change < 0:
                    declines += 1
                    
                ema20 = close.ewm(span=20).mean().iloc[-1]
                ema50 = close.ewm(span=50).mean().iloc[-1]
                
                if close.iloc[-1] > ema20:
                    above_ema20 += 1
                if close.iloc[-1] > ema50:
                    above_ema50 += 1
                    
                total += 1
            except Exception:
                continue
                
        if total == 0:
            return {'advances_ratio': 1.0, 'pct_above_ema20': 50.0, 'pct_above_ema50': 50.0, 'status': 'NEUTRAL'}
            
        pct_ema20 = round((above_ema20 / total) * 100, 1)
        pct_ema50 = round((above_ema50 / total) * 100, 1)
        adv_ratio = round(advances / max(1, declines), 2)
        
        status = 'STRONG' if pct_ema50 > 60 and adv_ratio > 1.2 else ('WEAK' if pct_ema50 < 40 else 'NEUTRAL')
        
        return {
            'advances_ratio': adv_ratio,
            'pct_above_ema20': pct_ema20,
            'pct_above_ema50': pct_ema50,
            'status': status
        }
    except Exception as e:
        logger.warning(f"Error calculating market breadth: {e}")
        return {'advances_ratio': 1.0, 'pct_above_ema20': 50.0, 'pct_above_ema50': 50.0, 'status': 'NEUTRAL'}

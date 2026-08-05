from datetime import date
import yfinance as yf
from src.performance.database import get_db_connection
from src.utils.logger import logger

def calculate_indian_tx_fees(entry_val: float, exit_val: float) -> float:
    """
    Calculates Indian Equity Delivery transaction costs:
    - STT: 0.1% on buy & sell
    - Exchange & Stamp Duty: ~0.02%
    - Total estimated fees ~ 0.25% of turnover
    """
    turnover = entry_val + exit_val
    return turnover * 0.0025

def evaluate_closed_trades():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM trades WHERE status = 'OPEN'")
        open_trades = cursor.fetchall()
        
        for trade in open_trades:
            trade_id = trade['id']
            ticker = trade['ticker']
            entry_price = trade['entry_price']
            target = trade['tp1']
            stoploss = trade['stoploss']
            entry_date_str = trade['entry_date']
            
            # Fetch subsequent historical candles strictly after entry_date (No look-ahead bias)
            hist = yf.Ticker(ticker).history(start=entry_date_str)
            if hist is None or len(hist) <= 1:
                continue
                
            future_candles = hist.iloc[1:]  # Only candles AFTER signal date
            
            hit_status = 'OPEN'
            exit_price = entry_price
            exit_date = None
            
            for dt, row in future_candles.iterrows():
                high = row['High']
                low = row['Low']
                close = row['Close']
                
                # Check low first for conservative SL trigger
                if low <= stoploss:
                    hit_status = 'STOPLOSS_HIT'
                    exit_price = stoploss
                    exit_date = dt.strftime('%Y-%m-%d')
                    break
                elif high >= target:
                    hit_status = 'TARGET_HIT'
                    exit_price = target
                    exit_date = dt.strftime('%Y-%m-%d')
                    break
                    
            if hit_status != 'OPEN':
                gross_pnl = exit_price - entry_price
                fees = calculate_indian_tx_fees(entry_price, exit_price)
                net_pnl = gross_pnl - fees
                
                cursor.execute('''
                UPDATE trades
                SET status = ?, exit_date = ?, exit_price = ?, pnl = ?
                WHERE id = ?
                ''', (hit_status, exit_date, exit_price, net_pnl, trade_id))
                
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error evaluating closed trades: {e}")

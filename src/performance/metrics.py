from src.performance.database import get_db_connection

def compute_historical_performance_metrics() -> dict:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM trades WHERE status != 'OPEN'")
        total = cursor.fetchone()['cnt']
        
        if total == 0:
            return {'total_trades': 0, 'win_rate': 0.0, 'calibration_sample': total}
            
        cursor.execute("SELECT COUNT(*) as cnt FROM trades WHERE status = 'TARGET_HIT'")
        wins = cursor.fetchone()['cnt']
        
        win_rate = round((wins / total) * 100.0, 1)
        conn.close()
        
        return {
            'total_trades': total,
            'win_rate': win_rate,
            'calibration_sample': total
        }
    except Exception:
        return {'total_trades': 0, 'win_rate': 0.0, 'calibration_sample': 0}

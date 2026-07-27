from datetime import date, timedelta
from ..database.supabase_client import get_supabase
from ..utils.logger import logger

def record_signal(ticker, signal_type, entry, target, stoploss, confidence, expiry_days=30):
    supabase = get_supabase()
    if not supabase:
        logger.warning("⚠️ Supabase not available, skipping signal recording.")
        return
    entry_date = date.today()
    expiry_date = entry_date + timedelta(days=expiry_days)
    try:
        supabase.table('backtest_results').insert({
            'ticker': ticker,
            'signal_type': signal_type,
            'entry_date': entry_date.isoformat(),
            'entry_price': entry,
            'target': target,
            'stoploss': stoploss,
            'confidence': confidence,
            'expiry_date': expiry_date.isoformat(),
            'status': 'open'
        }).execute()
    except Exception as e:
        logger.error(f"Failed to record signal: {e}")

def evaluate_closed_signals():
    supabase = get_supabase()
    if not supabase:
        logger.warning("⚠️ Supabase not available, skipping backtest evaluation.")
        return
    try:
        open_trades = supabase.table('backtest_results').select('*').eq('status', 'open').execute()
    except Exception as e:
        logger.error(f"Backtest fetch failed: {e}")
        return
    for trade in open_trades.data:
        ticker = trade['ticker']
        entry = trade['entry_price']
        target = trade['target']
        stoploss = trade['stoploss']
        expiry = trade['expiry_date']
        try:
            from ..fetchers.yahoo import fetch as yfetch
            hist, _ = yfetch(ticker, period=f"{max(1, (date.today() - date.fromisoformat(trade['entry_date'])).days)}d")
            if hist is None or hist.empty:
                continue
            current = hist['Close'].iloc[-1]
            if current >= target:
                status = 'target_hit'
            elif current <= stoploss:
                status = 'stoploss_hit'
            elif date.today() >= date.fromisoformat(expiry):
                status = 'expired'
            else:
                continue
            supabase.table('backtest_results').update({
                'exit_date': date.today().isoformat(),
                'exit_price': current,
                'status': status,
                'pnl': current - entry
            }).eq('id', trade['id']).execute()
        except Exception as e:
            logger.error(f"Error evaluating trade {ticker}: {e}")

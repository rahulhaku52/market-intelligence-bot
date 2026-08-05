import json
from datetime import date, datetime, timedelta
import pytz
from config.settings import SessionState

IST = pytz.timezone('Asia/Kolkata')

NSE_HOLIDAYS = [
    "2025-03-14", "2025-03-31", "2025-04-14", "2025-04-18", "2025-05-01",
    "2025-08-15", "2025-10-02", "2025-10-21", "2025-11-05", "2025-12-25",
    "2026-01-26", "2026-03-14", "2026-03-31", "2026-04-14", "2026-04-18",
    "2026-05-01", "2026-08-15", "2026-10-02", "2026-12-25"
]

def load_custom_holidays(filepath='config/nse_holidays.json'):
    try:
        with open(filepath, 'r') as f:
            extra = json.load(f)
            return extra.get("holidays", [])
    except Exception:
        return []

ALL_HOLIDAYS = set(NSE_HOLIDAYS + load_custom_holidays())

def get_current_session_state() -> SessionState:
    now = datetime.now(IST)
    today_str = now.strftime("%Y-%m-%d")
    
    if now.weekday() >= 5 or today_str in ALL_HOLIDAYS:
        return SessionState.HOLIDAY
        
    current_time = now.time()
    
    pre_start = datetime.strptime("09:00", "%H:%M").time()
    market_open = datetime.strptime("09:15", "%H:%M").time()
    market_close = datetime.strptime("15:30", "%H:%M").time()
    post_end = datetime.strptime("16:00", "%H:%M").time()
    
    if pre_start <= current_time < market_open:
        return SessionState.PRE_MARKET
    elif market_open <= current_time <= market_close:
        return SessionState.REGULAR
    elif market_close < current_time <= post_end:
        return SessionState.POST_MARKET
    else:
        return SessionState.CLOSED

def is_market_open() -> bool:
    return get_current_session_state() == SessionState.REGULAR

def next_trading_day() -> date:
    d = date.today() + timedelta(days=1)
    while d.weekday() >= 5 or d.isoformat() in ALL_HOLIDAYS:
        d += timedelta(days=1)
    return d
